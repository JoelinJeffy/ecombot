"""
history_service.py -- PostgreSQL-backed conversation history (Day 04)
----------------------------------------------------------------------
Stores durable conversation history for audit, replay, and analysis.
Separate from session state - this is permanent business record.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.services.db import execute_query

logger = logging.getLogger(__name__)


class HistoryService:
    """
    Service for storing and retrieving conversation history.
    Uses PostgreSQL for durable storage.
    """
    
    @staticmethod
    def save_turn(
        session_id: str,
        user_id: str,
        role: str,
        content: str,
        tool_calls: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Save a conversation turn to the database.
        
        Args:
            session_id: Unique session identifier
            user_id: User identifier
            role: Message role (user, assistant, system, tool)
            content: Message content
            tool_calls: Optional list of tool calls made
        """
        query = """
            INSERT INTO session_history 
            (session_id, user_id, role, content, tool_calls)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        try:
            tool_calls_json = json.dumps(tool_calls) if tool_calls else None
            execute_query(
                query,
                (session_id, user_id, role, content, tool_calls_json),
                fetch="none"
            )
            logger.debug(f"Saved turn for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to save conversation turn: {e}")
    
    @staticmethod
    def get_session_history(
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history for a session.
        
        Args:
            session_id: Session to retrieve
            limit: Optional limit on number of messages
        
        Returns:
            List of conversation turns
        """
        query = """
            SELECT id, session_id, user_id, role, content, tool_calls, created_at
            FROM session_history
            WHERE session_id = %s
            ORDER BY created_at ASC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            rows = execute_query(query, (session_id,), fetch="all")
            
            history = []
            for row in rows:
                tool_calls = None
                if row[5]:  # tool_calls column
                    try:
                        tool_calls = json.loads(row[5])
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse tool_calls for row {row[0]}")
                
                history.append({
                    "id": row[0],
                    "session_id": row[1],
                    "user_id": row[2],
                    "role": row[3],
                    "content": row[4],
                    "tool_calls": tool_calls,
                    "created_at": row[6]
                })
            
            return history
        except Exception as e:
            logger.error(f"Failed to get session history: {e}")
            return []
    
    @staticmethod
    def get_recent_history(
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent conversation turns for a user across all sessions.
        
        Args:
            user_id: User to retrieve history for
            limit: Maximum number of turns to return
        
        Returns:
            List of recent conversation turns
        """
        query = """
            SELECT id, session_id, user_id, role, content, tool_calls, created_at
            FROM session_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        
        try:
            rows = execute_query(query, (user_id, limit), fetch="all")
            
            history = []
            for row in rows:
                tool_calls = None
                if row[5]:
                    try:
                        tool_calls = json.loads(row[5])
                    except json.JSONDecodeError:
                        pass
                
                history.append({
                    "id": row[0],
                    "session_id": row[1],
                    "user_id": row[2],
                    "role": row[3],
                    "content": row[4],
                    "tool_calls": tool_calls,
                    "created_at": row[6]
                })
            
            return history
        except Exception as e:
            logger.error(f"Failed to get recent history: {e}")
            return []
    
    @staticmethod
    def delete_session_history(session_id: str) -> None:
        """
        Delete all history for a session.
        Use with caution - this is permanent.
        """
        query = "DELETE FROM session_history WHERE session_id = %s"
        
        try:
            execute_query(query, (session_id,), fetch="none")
            logger.info(f"Deleted history for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to delete session history: {e}")
