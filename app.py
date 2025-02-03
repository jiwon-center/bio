from flask import Flask, render_template, jsonify
import pandas as pd
import os

app = Flask(__name__)

# CSV 파일 경로
CSV_FILE_PATH1 = "data/prospective_cohort/prospective_cohort_outlier_winsorized_240613.csv"


@app.route('/')
def index():
    # 서버에서 테마와 레이아웃 옵션을 결정합니다.
    options = {
        'colorScheme': 'dark',
        'enableFixedHeader': True,
        'enableFixedSidebar': False,
        'enableFixedFooter': False,
        'enableClosedSidebar': False,
        'enableMobileMenu': False,
        'enablePageTabsAlt': True,
    }
    return render_template('index.html', options=options)


def load_and_process_data1():
    try:
        if not os.path.exists(CSV_FILE_PATH1):
            print("Error: CSV file not found.")
            return {"CKD 1": 0, "CKD 2": 0}, 0
        
        df = pd.read_csv(CSV_FILE_PATH1)
        
        # CKD stage 컬럼이 존재하는지 확인 후 전처리
        if 'ckd_stage' in df.columns:
            df['ckd_stage'] = df['ckd_stage'].astype(str).str.strip()
            
            # CKD 단계별 환자 수 집계
            counts = {
                "CKD 1": int((df['ckd_stage'] == '1').sum()),
                "CKD 2": int((df['ckd_stage'] == '2').sum() + \
                         (df['ckd_stage'] == '3').sum() + \
                         (df['ckd_stage'] == '4').sum() + \
                         (df['ckd_stage'] == '5').sum())
            }
            
            total_patients = int(df['ckd_stage'].notnull().sum())
            
            print("Processed data:", counts, "Total patients:", total_patients)
            return counts, total_patients
        else:
            print("Error: 'ckd_stage' column missing in CSV.")
            return {"CKD 1": 0, "CKD 2": 0}, 0
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return {"CKD 1": 0, "CKD 2": 0}, 0

def load_and_process_data2():
    try:
        if not os.path.exists(CSV_FILE_PATH1):
            print("Error: CSV file not found.")
            return {category: 0 for category in [
                "Type 2 Diabetes", "Hypertension", "Hyperlipidemia", "Chronic Kidney Disease",
                "Angina pectoris", "Myocardial Infarction", "Heart Failure", "Stroke"
            ]}, 0
        
        df = pd.read_csv(CSV_FILE_PATH1)
        
        categories = [
            "Type 2 Diabetes", "Hypertension", "Hyperlipidemia", "Chronic Kidney Disease",
            "Angina pectoris", "Myocardial Infarction", "Heart Failure", "Stroke"
        ]
        counts = {category: 0 for category in categories}
        total_patients = len(df)
        
        if 'htn' in df.columns:
            counts["Hypertension"] = int(df['htn'].fillna(0).astype(str).str.strip().eq('1').sum())
        if 'hld' in df.columns:
            counts["Hyperlipidemia"] = int(df['hld'].fillna(0).astype(str).str.strip().eq('1').sum())
        if 'ckd_stage' in df.columns:
            counts["Chronic Kidney Disease"] = int(df['ckd_stage'].fillna(0).astype(str).str.strip().isin(['3', '4', '5']).sum())
        if 'angina' in df.columns:
            counts["Angina pectoris"] = int(df['angina'].fillna(0).astype(str).str.strip().eq('1').sum())
        if 'mi' in df.columns:
            counts["Myocardial Infarction"] = int(df['mi'].fillna(0).astype(str).str.strip().eq('1').sum())
        if 'hf' in df.columns:
            counts["Heart Failure"] = int(df['hf'].fillna(0).astype(str).str.strip().eq('1').sum())
        if 'stroke' in df.columns:
            counts["Stroke"] = int(df['stroke'].fillna(0).astype(str).str.strip().eq('1').sum())
        
        print("Processed data:", counts, "Total patients:", total_patients)
        return counts, total_patients
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return {category: 0 for category in categories}, 0

@app.route('/data1')
def get_data1():
    counts, total_patients = load_and_process_data1()
    
    response_data = {
        "categories": list(counts.keys()),
        "data": [int(value) for value in counts.values()],
        "total_patients": int(total_patients)
    }
    
    print("Response data:", response_data)
    return jsonify(response_data)

@app.route('/data2')
def get_data2():
    counts, total_patients = load_and_process_data2()
    
    sorted_data = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    sorted_categories = [item[0] for item in sorted_data]
    sorted_counts = [item[1] for item in sorted_data]
    
    response_data = {
        "categories": sorted_categories,
        "data": sorted_counts,
        "total_patients": int(total_patients)
    }
    
    print("Response data:", response_data)
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)