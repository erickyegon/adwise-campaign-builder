#!/usr/bin/env python3
"""
Test script for AdWise AI Application on port 8007
"""

import requests
import json

def test_application():
    """Test the AdWise AI application endpoints"""
    
    print('🧪 Testing AdWise AI Application Endpoints')
    print('=' * 50)

    base_url = 'http://127.0.0.1:8007'

    # Test main endpoints
    endpoints = [
        ('/', 'Main Application'),
        ('/health', 'Health Check'),
        ('/docs', 'API Documentation'),
        ('/api/v1/', 'API Root')
    ]

    all_working = True
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=5)
            if response.status_code == 200:
                status = '✅ WORKING'
                print(f'{name}: {status}')
            else:
                status = f'⚠️ Status: {response.status_code}'
                print(f'{name}: {status}')
                all_working = False
        except Exception as e:
            print(f'{name}: ❌ ERROR - {str(e)[:50]}...')
            all_working = False

    print('=' * 50)
    if all_working:
        print('🎯 Application Status: FULLY OPERATIONAL ✅')
    else:
        print('⚠️ Application Status: Some issues detected')
    
    return all_working

if __name__ == "__main__":
    test_application()
