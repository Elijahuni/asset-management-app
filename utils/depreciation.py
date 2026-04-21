from datetime import datetime
import pandas as pd

def calculate_residual_value(purchase_date, purchase_price, lifespan_years=5):
    """
    정액법(Straight-line)을 이용한 자산 현재 잔존 가치 계산.
    구매일로부터 매일 일정하게 가치가 하락하며, 내용연수(보통 5년) 경과 시 잔존가치는 0원이 됩니다.
    """
    if pd.isnull(purchase_date) or pd.isnull(purchase_price):
        return 0
        
    try:
        # 문자열인 경우 datetime 으로 파싱
        if isinstance(purchase_date, str):
            p_date = datetime.strptime(purchase_date, "%Y-%m-%d").date()
        else:
            # Timestamp 나 여타 타입인 경우
            p_date = pd.to_datetime(purchase_date).date()
            
        today = datetime.now().date()
        
        # 총 예상 수명(일수 환산) - 윤년 무시 365일 기준
        total_lifespan_days = lifespan_years * 365
        
        # 구매일로부터 경과한 일수
        elapsed_days = (today - p_date).days
        
        # 구매 전이거나 아직 날짜가 미래인 경우 (에러 방지)
        if elapsed_days < 0:
            return float(purchase_price)
            
        # 잔존 가치가 0 이하인 경우 (내용 연수 초과)
        if elapsed_days >= total_lifespan_days:
            return 0.0
            
        # 정액법 남은 가치 비율 계산
        residual_ratio = 1.0 - (elapsed_days / total_lifespan_days)
        residual_value = float(purchase_price) * residual_ratio
        
        return round(residual_value)
    except Exception:
        return 0
