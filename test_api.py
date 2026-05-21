#!/usr/bin/env python3
"""
Sauti ya Mwananchi - Local API Test Script
Test the API endpoints without needing WhatsApp or Africa's Talking
"""

import json
import requests
import sys
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30

# ANSI colors for output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print section header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}")
    print(f"{text.center(60)}")
    print(f"{'=' * 60}{Colors.END}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")


def print_request(method: str, endpoint: str, data: Dict = None):
    """Print request details."""
    print(f"{Colors.BLUE}{method} {endpoint}{Colors.END}")
    if data:
        print(f"{Colors.YELLOW}Payload:{Colors.END} {json.dumps(data, indent=2)}")


def print_response(response: Dict[str, Any], status_code: int):
    """Print response details."""
    print(f"{Colors.GREEN}Status: {status_code}{Colors.END}")
    print(f"{Colors.YELLOW}Response:{Colors.END}")
    print(json.dumps(response, indent=2))


def test_health() -> bool:
    """Test /health endpoint."""
    print_header("TEST 1: Health Check")
    
    try:
        print_request("GET", "/health")
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        response.raise_for_status()
        print_response(response.json(), response.status_code)
        print_success("Server is healthy!")
        return True
    except requests.exceptions.ConnectionError:
        print_error(f"Could not connect to {BASE_URL}")
        print_info("Make sure the server is running: python main.py")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_about() -> bool:
    """Test /about endpoint."""
    print_header("TEST 2: About Service")
    
    try:
        print_request("GET", "/about")
        response = requests.get(f"{BASE_URL}/about", timeout=TIMEOUT)
        response.raise_for_status()
        print_response(response.json(), response.status_code)
        print_success("Service information retrieved!")
        return True
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_message(question: str, lang: str = "auto") -> bool:
    """Test /message endpoint."""
    print_header(f"TEST 3: Message Endpoint - {lang.upper()}")
    
    try:
        payload = {
            "phone": "+254700000000",
            "message": question
        }
        print_request("POST", "/message", payload)
        response = requests.post(
            f"{BASE_URL}/message",
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        result = response.json()
        print_response(result, response.status_code)
        
        if "reply" in result:
            print_success("Got reply from agent!")
            print(f"\n{Colors.BOLD}Agent Reply:{Colors.END}\n{result['reply']}\n")
        return True
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_fact_check(claim: str) -> bool:
    """Test fact-checking."""
    print_header(f"TEST 4: Fact Check")
    
    try:
        payload = {
            "phone": "+254700000000",
            "message": f"Is it true that {claim}?"
        }
        print_request("POST", "/message", payload)
        response = requests.post(
            f"{BASE_URL}/message",
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        result = response.json()
        print_response(result, response.status_code)
        
        if "reply" in result:
            print_success("Fact-check result received!")
            print(f"\n{Colors.BOLD}Verdict:{Colors.END}\n{result['reply']}\n")
        return True
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_location(area: str) -> bool:
    """Test polling location lookup."""
    print_header(f"TEST 5: Polling Location - {area}")
    
    try:
        payload = {
            "phone": "+254700000000",
            "message": f"Where do I vote in {area}?"
        }
        print_request("POST", "/message", payload)
        response = requests.post(
            f"{BASE_URL}/message",
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        result = response.json()
        print_response(result, response.status_code)
        
        if "reply" in result:
            print_success("Location results received!")
            print(f"\n{Colors.BOLD}Polling Stations:{Colors.END}\n{result['reply']}\n")
        return True
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_sms_endpoint() -> bool:
    """Test /send-sms endpoint."""
    print_header("TEST 6: Send SMS Endpoint")
    
    try:
        payload = {
            "phone": "+254700000000",
            "message": "This is a test message"
        }
        print_request("POST", "/send-sms", payload)
        response = requests.post(
            f"{BASE_URL}/send-sms",
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        result = response.json()
        print_response(result, response.status_code)
        print_info("Note: Africa's Talking credentials required for actual SMS sending")
        return True
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_ussd_endpoint() -> bool:
    """Test /ussd endpoint."""
    print_header("TEST 7: USSD Endpoint (Menu)")
    
    try:
        payload = {
            "session_id": "demo-session",
            "phone": "+254700000000",
            "text": ""
        }
        print_request("POST", "/ussd", payload)
        response = requests.post(
            f"{BASE_URL}/ussd",
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        result = response.json()
        print_response(result, response.status_code)
        print_success("USSD menu received!")
        return True
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def interactive_mode():
    """Run in interactive mode."""
    print_header("INTERACTIVE MODE")
    print_info("Commands:")
    print_info("  1 - Message (English)")
    print_info("  2 - Message (Kiswahili)")
    print_info("  3 - Fact Check")
    print_info("  4 - Polling Location")
    print_info("  5 - Send SMS")
    print_info("  6 - USSD Menu")
    print_info("  q - Quit")
    
    while True:
        choice = input(f"\n{Colors.BOLD}Choose test (1-6, q to quit): {Colors.END}").strip().lower()
        
        if choice == "q":
            break
        elif choice == "1":
            msg = input("Enter message (English): ")
            test_message(msg, "en")
        elif choice == "2":
            msg = input("Enter message (Kiswahili): ")
            test_message(msg, "sw")
        elif choice == "3":
            claim = input("Enter claim to check: ")
            test_fact_check(claim)
        elif choice == "4":
            area = input("Enter area/constituency: ")
            test_location(area)
        elif choice == "5":
            test_sms_endpoint()
        elif choice == "6":
            test_ussd_endpoint()
        else:
            print_error("Invalid choice")


def main():
    """Run all tests."""
    print(f"{Colors.BOLD}{Colors.HEADER}")
    print("╔" + "=" * 58 + "╗")
    print("║" + "SAUTI YA MWANANCHI - LOCAL API TEST SUITE".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    print(f"{Colors.END}\n")
    
    # Check if interactive mode requested
    interactive = "--interactive" in sys.argv or "-i" in sys.argv
    
    if interactive:
        # Test health first
        if not test_health():
            sys.exit(1)
        
        # Go to interactive mode
        interactive_mode()
    else:
        # Run full test suite
        print_info("Running full test suite...\n")
        
        tests = [
            ("Health Check", test_health),
            ("Service Info", test_about),
            ("English Message", lambda: test_message("What are my voting rights?", "en")),
            ("Kiswahili Message", lambda: test_message("Ni haki gani ninazopata siku ya uchaguzi?", "sw")),
            ("Fact Check", lambda: test_fact_check("voting is compulsory")),
            ("Location Lookup", lambda: test_location("Westlands")),
            ("SMS Endpoint", test_sms_endpoint),
            ("USSD Menu", test_ussd_endpoint),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print_error(f"Unexpected error in {test_name}: {e}")
                failed += 1
        
        # Summary
        print_header("TEST SUMMARY")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
        if failed > 0:
            print(f"{Colors.RED}Failed: {failed}{Colors.END}")
        else:
            print_success("All tests passed!")
        
        print_info(f"Total: {passed + failed} tests")
        
        # Next steps
        print_header("NEXT STEPS")
        print_info("1. Run interactive tests: python test_api.py --interactive")
        print_info("2. Start ngrok: ./setup-ngrok.ps1")
        print_info("3. Configure Africa's Talking webhook")
        print_info("4. Send WhatsApp message to test!")
        print_info("")
        print_info("Documentation: WHATSAPP_QUICKSTART.md")
        print("")


if __name__ == "__main__":
    main()
