-- 0. 기존 테이블 삭제 (초기화용)
DROP TABLE IF EXISTS rentals CASCADE;
DROP TABLE IF EXISTS asset_history CASCADE;
DROP TABLE IF EXISTS assets CASCADE;

-- 1. 자산 테이블
CREATE TABLE assets (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    asset_number VARCHAR UNIQUE NOT NULL, -- 예: AST-20231015-001
    name VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    department VARCHAR NOT NULL,
    assignee VARCHAR,
    purchase_date DATE,
    purchase_price NUMERIC,
    location VARCHAR,
    status VARCHAR DEFAULT '정상',
    warranty_expiry_date DATE,
    next_maintenance_date DATE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 대여 기록 테이블
CREATE TABLE rentals (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,
    renter VARCHAR NOT NULL,
    rental_date DATE NOT NULL,
    expected_return_date DATE NOT NULL,
    actual_return_date DATE,
    status VARCHAR DEFAULT '대여중',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 이력 기록 테이블
CREATE TABLE asset_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,
    change_type VARCHAR NOT NULL, -- '등록', '상태변경', '부서변경' 등
    description TEXT,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==============================================
-- [수정] RLS(Row Level Security) 활성화 및 Auth 정책 추가
-- ==============================================
-- 로그인한 사용자만 자산 데이터에 접근할 수 있도록 권한을 설정합니다.
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE rentals ENABLE ROW LEVEL SECURITY;
ALTER TABLE asset_history ENABLE ROW LEVEL SECURITY;

-- 로그인된 사용자(authenticated)에게 모든 권한(SELECT, INSERT, UPDATE, DELETE) 부여
DROP POLICY IF EXISTS "Allow all for authenticated on assets" ON assets;
CREATE POLICY "Allow all for authenticated on assets" ON assets FOR ALL USING (auth.role() = 'authenticated');

DROP POLICY IF EXISTS "Allow all for authenticated on rentals" ON rentals;
CREATE POLICY "Allow all for authenticated on rentals" ON rentals FOR ALL USING (auth.role() = 'authenticated');

DROP POLICY IF EXISTS "Allow all for authenticated on asset_history" ON asset_history;
CREATE POLICY "Allow all for authenticated on asset_history" ON asset_history FOR ALL USING (auth.role() = 'authenticated');
