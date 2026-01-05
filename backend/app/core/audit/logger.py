"""Immutable audit logging service for compliance"""

from datetime import datetime
from typing import Dict, Any, Optional
from decimal import Decimal
import hashlib
import json
import logging
from uuid import UUID

from app.core.database import get_service_db
from app.config import settings

logger = logging.getLogger(__name__)


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder for Decimal types"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


class AuditLogger:
    """
    Append-only audit logging service
    
    All analysis events, risk decisions, and recommendations are logged
    for regulatory compliance and legal defensibility.
    """
    
    @staticmethod
    def compute_hash(data: Dict[str, Any]) -> str:
        """
        Compute SHA256 hash of data for integrity verification
        
        Args:
            data: Dictionary to hash
        
        Returns:
            Hex string of SHA256 hash
        """
        canonical = json.dumps(data, sort_keys=True, default=str, cls=DecimalEncoder)
        return hashlib.sha256(canonical.encode()).hexdigest()
    
    @staticmethod
    async def log_event(
        event_type: str,
        user_id: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        ticker: Optional[str] = None,
        signal_type: Optional[str] = None,
        confidence_score: Optional[float] = None,
        risk_level: Optional[str] = None,
        was_actionable: Optional[bool] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log an event to audit logs (immutable)
        
        Args:
            event_type: Type of event (e.g., 'signal_generated')
            user_id: UUID of user
            input_data: Input parameters/data
            output_data: Output results/data
            session_id: Session UUID
            ip_address: Client IP address
            user_agent: Client user agent string
            ticker: Stock ticker if applicable
            signal_type: Signal type if applicable
            confidence_score: Confidence score if applicable
            risk_level: Risk level if applicable
            was_actionable: Whether recommendation was actionable
            metadata: Additional context
        
        Returns:
            UUID of created audit log entry
        """
        try:
            # Convert Decimal values to strings for JSON serialization
            def convert_decimals(obj):
                if isinstance(obj, Decimal):
                    return str(obj)
                elif isinstance(obj, dict):
                    return {k: convert_decimals(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_decimals(item) for item in obj]
                return obj
            
            # Compute hashes for integrity
            input_hash = AuditLogger.compute_hash(input_data)
            output_hash = AuditLogger.compute_hash(output_data)
            
            # Prepare log entry with converted Decimal values
            log_entry = {
                "event_type": event_type,
                "user_id": str(user_id),
                "session_id": str(session_id) if session_id else None,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "input_data": convert_decimals(input_data),
                "input_hash": input_hash,
                "output_data": convert_decimals(output_data),
                "output_hash": output_hash,
                "ticker": ticker,
                "signal_type": signal_type,
                "confidence_score": confidence_score,
                "risk_level": risk_level,
                "was_actionable": was_actionable,
                "compliance_version": settings.TERMS_VERSION,
                "model_version": settings.VERSION,
                "metadata": metadata or {}
            }
            
            # Insert into audit_logs table (using service role to bypass RLS)
            db = get_service_db()
            result = db.table("audit_logs").insert(log_entry).execute()
            
            if result.data and len(result.data) > 0:
                log_id = result.data[0]["id"]
                logger.info(f"Audit log created: {log_id} | Event: {event_type} | User: {user_id}")
                return log_id
            else:
                logger.error(f"Failed to create audit log for event: {event_type}")
                return None
                
        except Exception as e:
            # CRITICAL: Audit logging failure should not block operations
            # but must be logged for investigation
            logger.error(f"CRITICAL: Audit logging failed: {e}", exc_info=True)
            # In production, send alert to monitoring system
            return None
    
    @staticmethod
    async def log_analysis_requested(
        user_id: str,
        ticker: str,
        input_params: Dict[str, Any],
        full_response: Dict[str, Any],
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """Log analysis request"""
        return await AuditLogger.log_event(
            event_type="analysis",
            user_id=user_id,
            input_data={
                "ticker": ticker,
                "params": input_params
            },
            output_data=full_response,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            ticker=ticker
        )
    
    @staticmethod
    async def log_signal_generated(
        user_id: str,
        ticker: str,
        signal_data: Dict[str, Any],
        indicators: Dict[str, Any],
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """Log signal generation"""
        return await AuditLogger.log_event(
            event_type="signal",
            user_id=user_id,
            input_data={
                "ticker": ticker,
                "indicators": indicators
            },
            output_data=signal_data,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            ticker=ticker,
            signal_type=signal_data.get("signal_type"),
            confidence_score=signal_data.get("confidence")
        )
    
    @staticmethod
    async def log_risk_assessment(
        user_id: str,
        ticker: str,
        signal_data: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        user_profile: Dict[str, Any],
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """Log risk assessment"""
        return await AuditLogger.log_event(
            event_type="risk",
            user_id=user_id,
            input_data={
                "ticker": ticker,
                "signal": signal_data,
                "user_profile": user_profile
            },
            output_data=risk_assessment,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            ticker=ticker,
            signal_type=signal_data.get("signal_type"),
            confidence_score=signal_data.get("confidence"),
            risk_level=risk_assessment.get("overall_risk"),
            was_actionable=risk_assessment.get("is_actionable")
        )
    
    @staticmethod
    async def log_user_login(
        user_id: str,
        session_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True
    ) -> str:
        """Log user login attempt"""
        return await AuditLogger.log_event(
            event_type="user_login",
            user_id=user_id,
            input_data={
                "timestamp": datetime.utcnow().isoformat()
            },
            output_data={
                "success": success,
                "session_id": session_id
            },
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    async def log_risk_profile_updated(
        user_id: str,
        old_profile: Dict[str, Any],
        new_profile: Dict[str, Any],
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """Log risk profile update"""
        return await AuditLogger.log_event(
            event_type="risk_profile_updated",
            user_id=user_id,
            input_data={
                "old_profile": old_profile
            },
            output_data={
                "new_profile": new_profile
            },
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
