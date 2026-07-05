"""
db.py -- PostgreSQL database connection pool (Day 04)
------------------------------------------------------
Provides reusable database access for tools and services.
Uses connection pooling for performance and proper error handling.
"""

import logging 
from contextlib import contextmanager 
from typing import Any ,Generator ,Optional 

import psycopg2 
from psycopg2 import pool 

from src .config .settings import get_postgres_dsn 

logger =logging .getLogger (__name__ )


_connection_pool :Optional [pool .SimpleConnectionPool ]=None 


def init_db_pool (min_conn :int =1 ,max_conn :int =10 )->None :
    """
    Initialize the PostgreSQL connection pool.
    Should be called once at application startup.
    """
    global _connection_pool 

    if _connection_pool is not None :
        logger .warning ("Database pool already initialized")
        return 

    try :
        _connection_pool =pool .SimpleConnectionPool (
        min_conn ,
        max_conn ,
        get_postgres_dsn ()
        )
        logger .info ("PostgreSQL connection pool initialized")
    except psycopg2 .Error as e :
        logger .error (f"Failed to initialize database pool: {e }")
        raise RuntimeError (f"Database initialization failed: {e }")


def close_db_pool ()->None :
    """
    Close all connections in the pool.
    Should be called at application shutdown.
    """
    global _connection_pool 

    if _connection_pool is not None :
        _connection_pool .closeall ()
        _connection_pool =None 
        logger .info ("PostgreSQL connection pool closed")


@contextmanager 
def get_db_connection ()->Generator [Any ,None ,None ]:
    """
    Context manager for database connections.
    Automatically returns connection to pool when done.
    
    Usage:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM orders")
                results = cur.fetchall()
    """
    if _connection_pool is None :
        init_db_pool ()

    conn =None 
    try :
        conn =_connection_pool .getconn ()
        yield conn 
        conn .commit ()
    except psycopg2 .Error as e :
        if conn :
            conn .rollback ()
        logger .error (f"Database error: {e }")
        raise 
    finally :
        if conn :
            _connection_pool .putconn (conn )


def execute_query (query :str ,params :tuple =None ,fetch :str ="all")->Any :
    """
    Execute a SQL query and return results.
    
    Args:
        query: SQL query string
        params: Query parameters (tuple)
        fetch: 'one', 'all', or 'none'
    
    Returns:
        Query results or None for non-SELECT queries
    """
    with get_db_connection ()as conn :
        with conn .cursor ()as cur :
            cur .execute (query ,params )

            if fetch =="one":
                return cur .fetchone ()
            elif fetch =="all":
                return cur .fetchall ()
            else :
                return None 
