#!/usr/bin/env python3
"""
View session history from PostgreSQL.
Usage: python scripts/view_history.py <session_id>
"""

import sys 
from pathlib import Path 


sys .path .insert (0 ,str (Path (__file__ ).resolve ().parents [1 ]))

from src .services .db import init_db_pool 
from src .services .history_service import HistoryService 


def main ():
    if len (sys .argv )<2 :
        print ("Usage: python scripts/view_history.py <session_id>")
        sys .exit (1 )

    session_id =sys .argv [1 ]

    try :
        init_db_pool ()
        history =HistoryService .get_session_history (session_id )

        if not history :
            print (f"No history found for session: {session_id }")
            return 

        print (f"\n{'='*70 }")
        print (f"Session History: {session_id }")
        print (f"{'='*70 }\n")

        for turn in history :
            print (f"[{turn ['created_at']}] {turn ['role'].upper ()}")
            print (f"  {turn ['content'][:200 ]}...")
            if turn ['tool_calls']:
                print (f"  Tool calls: {turn ['tool_calls']}")
            print ()

    except Exception as e :
        print (f"Error: {e }")
        sys .exit (1 )


if __name__ =="__main__":
    main ()
