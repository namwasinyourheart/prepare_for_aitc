import sys
sys.path.append("/home/nampv1/projects/prepare_for_aitc/")

from src.api_services.btc_api_client import *

# Gọi hàm để kiểm tra chi tiêu
info = kiem_tra_chi_tieu()

print(info)
