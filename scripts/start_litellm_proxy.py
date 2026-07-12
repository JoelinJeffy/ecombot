#!/usr/bin/env python3
"""
start_litellm_proxy.py -- Start LiteLLM proxy server for eComBot v4 (Day 07)
-----------------------------------------------------------------------------
Starts the LiteLLM proxy with the eComBot configuration, managing model
groups and fallback routing.

Usage:
    python scripts/start_litellm_proxy.py

Environment variables:
    OPENROUTER_API_KEY: Your OpenRouter API key (required)
    LITELLM_PORT: Port for proxy server (default: 4000)
    LITELLM_LOG_LEVEL: Logging level (default: INFO)

The proxy will be accessible at:
    http://localhost:4000
"""

import logging 
import os 
import subprocess 
import sys 
from pathlib import Path 
from dotenv import load_dotenv 


load_dotenv ()

logging .basicConfig (level =logging .INFO ,format ='%(levelname)s: %(message)s')
logger =logging .getLogger (__name__ )

PROJECT_ROOT =Path (__file__ ).resolve ().parents [1 ]
CONFIG_FILE =PROJECT_ROOT /"config"/"litellm_config.yaml"


def check_prerequisites ():
    """Check that all prerequisites are met."""
    errors =[]


    if not os .getenv ("OPENROUTER_API_KEY"):
        errors .append (
        "OPENROUTER_API_KEY not set. "
        "Add it to your .env file or export it."
        )


    if not CONFIG_FILE .exists ():
        errors .append (
        f"LiteLLM config file not found: {CONFIG_FILE }\n"
        "Run this script from the project root or check config/ directory."
        )


    try :
        import litellm 

        try :
            version =litellm .__version__ 
            logger .info (f"✓ LiteLLM version: {version }")
        except AttributeError :
            logger .info ("✓ LiteLLM installed")
    except ImportError :
        errors .append (
        "LiteLLM not installed. Install with: pip install 'litellm[proxy]'"
        )

    if errors :
        logger .error ("Prerequisites check failed:\n")
        for error in errors :
            logger .error (f"  ✗ {error }")
        sys .exit (1 )

    logger .info ("✓ All prerequisites met")


def start_proxy ():
    """Start the LiteLLM proxy server."""
    port =os .getenv ("LITELLM_PORT","4000")
    log_level =os .getenv ("LITELLM_LOG_LEVEL","INFO")

    logger .info (f"Starting LiteLLM proxy on port {port }...")
    logger .info (f"Config file: {CONFIG_FILE }")
    logger .info (f"Log level: {log_level }")


    cmd =[
    "litellm",
    "--config",str (CONFIG_FILE ),
    "--port",str (port ),
    "--detailed_debug"if log_level =="DEBUG"else "--num_workers","4"
    ]

    logger .info (f"Command: {' '.join (cmd )}\n")
    logger .info ("="*70 )
    logger .info ("LiteLLM Proxy Starting...")
    logger .info ("="*70 )
    logger .info (f"Proxy URL: http://localhost:{port }")
    logger .info ("Model Groups:")
    logger .info ("  - fast-faq: Lightweight models for simple queries")
    logger .info ("  - deep-support: Capable models for complex queries")
    logger .info ("\nPress Ctrl+C to stop the proxy")
    logger .info ("="*70 +"\n")

    try :

        subprocess .run (cmd ,cwd =str (PROJECT_ROOT ))
    except KeyboardInterrupt :
        logger .info ("\n\nProxy shutdown requested...")
    except Exception as e :
        logger .error (f"Failed to start proxy: {e }")
        sys .exit (1 )


def main ():
    """Main entry point."""
    logger .info ("="*70 )
    logger .info ("eComBot v4 - LiteLLM Proxy Startup")
    logger .info ("="*70 +"\n")

    check_prerequisites ()
    start_proxy ()

    logger .info ("\n✓ Proxy stopped cleanly")


if __name__ =="__main__":
    main ()
