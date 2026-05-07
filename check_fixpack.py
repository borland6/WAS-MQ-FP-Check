#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSphere Application Server 和 IBM MQ Fixpack 版本檢查工具
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from typing import Dict, List, Optional
import sys

class FixpackChecker:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.current_date = datetime.now()
        
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """解析日期字串，支援多種格式"""
        date_formats = [
            '%d %B %Y',      # 01 January 2024
            '%B %d, %Y',     # January 01, 2024
            '%Y-%m-%d',      # 2024-01-01
            '%d %b %Y',      # 01 Jan 2024
            '%b %d, %Y',     # Jan 01, 2024
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                return parsed_date
            except ValueError:
                continue
        return None
    
    def is_future_date(self, date_obj: datetime) -> bool:
        """檢查日期是否為未來日期"""
        return date_obj > self.current_date
    
    def check_websphere(self) -> Dict:
        """檢查 WebSphere Application Server 的最新 Fixpack"""
        url = "https://www.ibm.com/support/pages/recommended-updates-websphere-application-server"
        result = {
            'v9.0': {'version': 'N/A', 'date': 'N/A', 'status': 'error'},
            'v8.5': {'version': 'N/A', 'date': 'N/A', 'status': 'error'}
        }
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            text_content = soup.get_text()
            lines = text_content.split('\n')
            
            # 收集所有 9.0 的 Fixpack 資訊
            v90_fixpacks = []
            # 使用正則表達式在整個文本中搜尋
            # 格式: Fix pack XX9.0.5.XXDD Month YYYY
            pattern_v90 = r'Fix pack (\d+)9\.0\.5\.\1(\d{1,2}\s+\w+\s+\d{4})'
            for match in re.finditer(pattern_v90, text_content):
                fp_num = match.group(1)
                date_str = match.group(2)
                date_obj = self.parse_date(date_str)
                if date_obj:
                    v90_fixpacks.append({
                        'fp_num': int(fp_num),
                        'version': f'9.0.5.{fp_num}',
                        'date': date_obj,
                        'date_str': date_obj.strftime('%Y-%m-%d'),
                        'is_future': self.is_future_date(date_obj)
                    })
            
            # 找出最新的非未來日期版本
            valid_v90 = [fp for fp in v90_fixpacks if not fp['is_future']]
            if valid_v90:
                latest_v90 = max(valid_v90, key=lambda x: x['fp_num'])
                result['v9.0'] = {
                    'version': f"Fix Pack {latest_v90['fp_num']} ({latest_v90['version']})",
                    'date': latest_v90['date_str'],
                    'status': 'success'
                }
            
            # 收集所有 8.5 的 Fixpack 資訊
            v85_fixpacks = []
            # 使用正則表達式在整個文本中搜尋
            # 格式: Fix pack XX8.5.5.XXDD Month YYYY
            pattern_v85 = r'Fix pack (\d+)8\.5\.5\.\1(\d{1,2}\s+\w+\s+\d{4})'
            for match in re.finditer(pattern_v85, text_content):
                fp_num = match.group(1)
                date_str = match.group(2)
                date_obj = self.parse_date(date_str)
                if date_obj:
                    v85_fixpacks.append({
                        'fp_num': int(fp_num),
                        'version': f'8.5.5.{fp_num}',
                        'date': date_obj,
                        'date_str': date_obj.strftime('%Y-%m-%d'),
                        'is_future': self.is_future_date(date_obj)
                    })
            
            # 找出最新的非未來日期版本
            valid_v85 = [fp for fp in v85_fixpacks if not fp['is_future']]
            if valid_v85:
                latest_v85 = max(valid_v85, key=lambda x: x['fp_num'])
                result['v8.5'] = {
                    'version': f"Fix Pack {latest_v85['fp_num']} ({latest_v85['version']})",
                    'date': latest_v85['date_str'],
                    'status': 'success'
                }
                                    
        except Exception as e:
            print(f"檢查 WebSphere 時發生錯誤: {str(e)}")
            result['v9.0']['status'] = f'error: {str(e)}'
            result['v8.5']['status'] = f'error: {str(e)}'
        
        return result
    
    def check_mq(self, version: str, url: str) -> Dict:
        """檢查 IBM MQ 的最新 Fixpack"""
        result = {
            'version': 'N/A',
            'date': 'N/A',
            'status': 'error'
        }
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            text_content = soup.get_text()
            lines = text_content.split('\n')
            
            # 收集所有 Fixpack 資訊
            fixpacks = []
            for i, line in enumerate(lines):
                # 尋找包含 IBM MQ 版本號的行
                if f'IBM MQ {version}' in line or f'MQ {version}' in line:
                    # 查找版本號和日期
                    version_match = re.search(rf'IBM MQ {version}\.0\.(\d+)', line)
                    if version_match:
                        patch_num = version_match.group(1)
                        # 查找日期（通常在附近幾行）
                        for j in range(max(0, i-2), min(i+10, len(lines))):
                            date_match = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', lines[j])
                            if date_match:
                                date_str = date_match.group(1)
                                date_obj = self.parse_date(date_str)
                                if date_obj:
                                    fixpacks.append({
                                        'patch_num': int(patch_num),
                                        'version': f'{version}.0.{patch_num}',
                                        'date': date_obj,
                                        'date_str': date_obj.strftime('%Y-%m-%d'),
                                        'is_future': self.is_future_date(date_obj)
                                    })
                                break
            
            # 找出最新的非未來日期版本
            valid_fixpacks = [fp for fp in fixpacks if not fp['is_future']]
            if valid_fixpacks:
                latest = max(valid_fixpacks, key=lambda x: x['patch_num'])
                result = {
                    'version': f"IBM MQ {latest['version']}",
                    'date': latest['date_str'],
                    'status': 'success'
                }
                return result
            
            # 如果上面的方法沒找到，嘗試從表格中提取
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    row_text = ' '.join([cell.get_text() for cell in cells])
                    
                    if version in row_text and ('Fix Pack' in row_text or 'Fixpack' in row_text or 'Cumulative' in row_text):
                        fp_version = None
                        date_str = None
                        
                        for cell in cells:
                            cell_text = cell.get_text().strip()
                            
                            if not fp_version:
                                version_match = re.search(rf'{version}\.0\.(\d+)', cell_text)
                                if version_match:
                                    fp_version = f"{version}.0.{version_match.group(1)}"
                            
                            if not date_str:
                                date_match = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', cell_text)
                                if date_match:
                                    date_str = date_match.group(1)
                        
                        if fp_version and date_str:
                            date_obj = self.parse_date(date_str)
                            if date_obj and not self.is_future_date(date_obj):
                                result = {
                                    'version': f'IBM MQ {fp_version}',
                                    'date': date_obj.strftime('%Y-%m-%d'),
                                    'status': 'success'
                                }
                                return result
                                
        except Exception as e:
            print(f"檢查 IBM MQ {version} 時發生錯誤: {str(e)}")
            result['status'] = f'error: {str(e)}'
        
        return result
    
    def generate_html_report(self, was_result: Dict, mq94_result: Dict, mq93_result: Dict, output_file: str):
        """生成 HTML 報告"""
        query_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebSphere & IBM MQ Fixpack 檢查報告</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            text-align: center;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #0066cc;
            margin-top: 30px;
            border-left: 4px solid #0066cc;
            padding-left: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th {{
            background-color: #0066cc;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .success {{
            color: #28a745;
            font-weight: bold;
        }}
        .error {{
            color: #dc3545;
            font-weight: bold;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background-color: white;
            border-top: 2px solid #0066cc;
            box-shadow: 0 -2px 4px rgba(0,0,0,0.1);
        }}
        .query-time {{
            font-size: 14px;
            color: #666;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }}
        .status-success {{
            background-color: #d4edda;
            color: #155724;
        }}
        .status-error {{
            background-color: #f8d7da;
            color: #721c24;
        }}
    </style>
</head>
<body>
    <h1>WebSphere Application Server & IBM MQ Fixpack 檢查報告</h1>
    
    <h2>WebSphere Application Server</h2>
    <table>
        <thead>
            <tr>
                <th>版本</th>
                <th>最新 Fixpack</th>
                <th>釋出日期</th>
                <th>狀態</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>V9.0</td>
                <td>{was_result['v9.0']['version']}</td>
                <td>{was_result['v9.0']['date']}</td>
                <td><span class="status-badge status-{was_result['v9.0']['status']}">{was_result['v9.0']['status']}</span></td>
            </tr>
            <tr>
                <td>V8.5</td>
                <td>{was_result['v8.5']['version']}</td>
                <td>{was_result['v8.5']['date']}</td>
                <td><span class="status-badge status-{was_result['v8.5']['status']}">{was_result['v8.5']['status']}</span></td>
            </tr>
        </tbody>
    </table>
    
    <h2>IBM MQ</h2>
    <table>
        <thead>
            <tr>
                <th>版本</th>
                <th>最新 Fixpack</th>
                <th>釋出日期</th>
                <th>狀態</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>V9.4</td>
                <td>{mq94_result['version']}</td>
                <td>{mq94_result['date']}</td>
                <td><span class="status-badge status-{mq94_result['status']}">{mq94_result['status']}</span></td>
            </tr>
            <tr>
                <td>V9.3</td>
                <td>{mq93_result['version']}</td>
                <td>{mq93_result['date']}</td>
                <td><span class="status-badge status-{mq93_result['status']}">{mq93_result['status']}</span></td>
            </tr>
        </tbody>
    </table>
    
    <div class="footer">
        <p class="query-time">查詢時間：{query_time}</p>
        <p style="font-size: 12px; color: #999;">本報告由自動化工具生成</p>
    </div>
</body>
</html>"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n報告已生成：{output_file}")

def main():
    print("開始檢查 WebSphere Application Server 和 IBM MQ 的最新 Fixpack...")
    print("=" * 70)
    
    checker = FixpackChecker()
    
    # 檢查 WebSphere Application Server
    print("\n正在檢查 WebSphere Application Server...")
    was_result = checker.check_websphere()
    print(f"  V9.0: {was_result['v9.0']['version']} ({was_result['v9.0']['date']})")
    print(f"  V8.5: {was_result['v8.5']['version']} ({was_result['v8.5']['date']})")
    
    # 檢查 IBM MQ 9.4
    print("\n正在檢查 IBM MQ 9.4...")
    mq94_url = "https://www.ibm.com/support/pages/node/7166037"
    mq94_result = checker.check_mq("9.4", mq94_url)
    print(f"  V9.4: {mq94_result['version']} ({mq94_result['date']})")
    
    # 檢查 IBM MQ 9.3
    print("\n正在檢查 IBM MQ 9.3...")
    mq93_url = "https://www.ibm.com/support/pages/node/6695813"
    mq93_result = checker.check_mq("9.3", mq93_url)
    print(f"  V9.3: {mq93_result['version']} ({mq93_result['date']})")
    
    # 生成 HTML 報告
    print("\n正在生成 HTML 報告...")
    output_file = "fp-check.html"
    checker.generate_html_report(was_result, mq94_result, mq93_result, output_file)
    
    print("\n" + "=" * 70)
    print("檢查完成！")

if __name__ == "__main__":
    main()

# Made with Bob
