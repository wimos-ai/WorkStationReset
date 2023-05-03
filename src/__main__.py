from recycle_bin_mgmnt import clear_recycle_bin
from folder_mgmnt import clear_downloads, clear_documents
from account_mgmnt import clear_work_school_accounts
from quick_access_mgmnt import clear_quick_access
from proc_mgr import kill_windowed_processes

if __name__ == "__main__":
    clear_downloads()
    clear_documents()
    clear_recycle_bin()
    clear_work_school_accounts()
    clear_quick_access()
    kill_windowed_processes()
    input()
    
    
