import os
import winreg

print("--- 1. os.environ check ---")
key_val = os.environ.get("GEMINI_API_KEY", "")
print("os.environ['GEMINI_API_KEY'] present:", bool(key_val))
print("Key length:", len(key_val))

print("\n--- 2. Windows HKCU Environment check ---")
try:
    hkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment")
    val, _ = winreg.QueryValueEx(hkey, "GEMINI_API_KEY")
    print("HKCU GEMINI_API_KEY present: True, length:", len(val))
except Exception as e:
    print("HKCU error:", e)

print("\n--- 3. Windows HKLM Environment check ---")
try:
    hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")
    val, _ = winreg.QueryValueEx(hkey, "GEMINI_API_KEY")
    print("HKLM GEMINI_API_KEY present: True, length:", len(val))
except Exception as e:
    print("HKLM error:", e)
