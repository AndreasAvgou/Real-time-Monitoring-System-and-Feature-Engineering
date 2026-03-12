import time
import logging
from fastapi import FastAPI, Depends, Request, Response, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from . import models, schemas, database, utils, logger_config

# Logger
logger_config.setup_logging()
logger = logging.getLogger("feature-api")

app = FastAPI(title="Feature Engineering API")

# Database initialization
try:
    models.Base.metadata.create_all(bind=database.engine)
    logger.info("Database components initialized with RFC3339 support.")
except Exception as e:
    logger.error(f"Critical Database Error: {e}")

# Συνάρτηση για αποθήκευση στο παρασκήνιο
def save_features_to_db(transactional_entries, feature_entries):
    db = database.SessionLocal()
    try:
        for t_entry in transactional_entries:
            db.add(t_entry)
        for f_entry in feature_entries:
            db.add(f_entry)
        db.commit()
    except Exception as e:
        logger.error(f"Background Save Error: {e}")
    finally:
        db.close()

# Middleware for Monitoring & Metrics
@app.middleware("http")
async def monitoring_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    
    latency = time.perf_counter() - start_time
    sys_metrics = utils.get_system_metrics()
    zero_vals = int(response.headers.get("X-Zero-Count", 0))

    db = database.SessionLocal()
    try:
        metric_entry = models.MetricLog(
            endpoint=request.url.path,
            latency=latency,
            cpu_usage=sys_metrics["cpu_usage"],
            memory_usage=sys_metrics["memory_usage"],
            zero_value_count=zero_vals,
            status_code=response.status_code
        )
        db.add(metric_entry)
        db.commit()
    except Exception as e:
        logger.error(f"Metrics logging failed: {e}")
    finally:
        db.close()
    return response

# 4. API Endpoints
@app.get("/health")
def health():
    return {"status": "UP"}

@app.post("/feature-engineering")
def process_features(
    payload: schemas.FeatureRequest, 
    response: Response, 
    background_tasks: BackgroundTasks, # Προσθήκη BackgroundTasks
    db: Session = Depends(database.get_db)
):
    zero_count = utils.perform_feature_engineering(payload.model_dump())
    results = []
    
    # Λίστες για προετοιμασία των εγγραφών
    transactional_to_save = []
    features_to_save = []

    try:
        for cust in payload.data:
            for loan in cust.loans:
                total = loan.amount + loan.fee
                ratio = total / loan.annual_income if loan.annual_income > 0 else 0
                
                # Δημιουργία αντικειμένων χωρίς άμεση προσθήκη στο db session του request
                transactional_to_save.append(
                    models.TransactionalData(customer_id=cust.customer_ID, **loan.model_dump())
                )
                features_to_save.append(
                    models.FeatureData(customer_id=cust.customer_ID, total_amount=total, income_ratio=ratio)
                )
                
                results.append({"customer_ID": cust.customer_ID, "total_amount": total, "income_ratio": ratio})
        
        # 🔥 Ανάθεση της αποθήκευσης στο παρασκήνιο
        background_tasks.add_task(save_features_to_db, transactional_to_save, features_to_save)
        
        response.headers["X-Zero-Count"] = str(zero_count)
        logger.info(f"Processed customer {payload.data[0].customer_ID}")
        return results
        
    except Exception as e:
        logger.error(f"Process Error: {e}")
        raise HTTPException(status_code=500, detail="Data processing failed")

@app.get("/customer/{cid}/history/transactional")
def get_transactional_history(cid: str, db: Session = Depends(database.get_db)):
    return db.query(models.TransactionalData).filter(models.TransactionalData.customer_id == cid).all()

@app.get("/customer/{cid}/history/features")
def get_feature_history(cid: str, db: Session = Depends(database.get_db)):
    return db.query(models.FeatureData).filter(models.FeatureData.customer_id == cid).all()

@app.delete("/customer/{cid}")
def delete_customer(cid: str, db: Session = Depends(database.get_db)):
    try:
        db.query(models.TransactionalData).filter(models.TransactionalData.customer_id == cid).delete()
        db.query(models.FeatureData).filter(models.FeatureData.customer_id == cid).delete()
        db.commit()
        logger.info(f"Customer {cid} purged.")
        return {"message": f"Customer {cid} deleted"}
    except Exception as e:
        db.rollback()
        logger.error(f"Delete failed: {e}")
        raise HTTPException(status_code=500, detail="Operation failed")