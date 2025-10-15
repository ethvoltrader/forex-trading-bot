# Testing Checklist - Forex Trading Bot

## ✅ Pre-Test Setup

- [ ] Virtual environment activated: `source venv/bin/activate`
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] config.yaml exists and is properly formatted
- [ ] logs/ directory will be created automatically

---

## 🧪 Test 1: Configuration System

**Test config_loader.py**

```bash
python config_loader.py
```

**Expected Results:**
- ✅ Configuration loaded successfully
- ✅ All test values print correctly (RSI period, capital, symbols)
- ✅ Validation passes
- ✅ Non-existent key returns default value
- ✅ Warning about missing secrets file (this is OK)

**Pass/Fail:** ___________

**Notes:**
_______________________________________________________

---

## 🧪 Test 2: Logger System

**Test logger_config.py**

```bash
python logger_config.py
```

**Expected Results:**
- ✅ logs/ directory created
- ✅ Log file created with timestamp
- ✅ Different log levels displayed (DEBUG, INFO, WARNING, ERROR)
- ✅ Console shows simpler output
- ✅ File contains detailed output

**Verify log file:**
```bash
cat logs/bot_*.log | tail -20
```

**Pass/Fail:** ___________

**Notes:**
_______________________________________________________

---

## 🧪 Test 3: Full Bot Test (Normal Operation)

**Run forex_test.py**

```bash
python forex_test.py
```

**Expected Results:**
- ✅ Configuration loaded
- ✅ Validation passes
- ✅ Logger initialized
- ✅ Fetches live forex prices
- ✅ Builds price history (19 data points)
- ✅ Calculates RSI for all pairs
- ✅ Generates trading signals (BUY/SELL/HOLD)
- ✅ No crashes or errors
- ✅ Clean exit

**Check for:**
- Capital: $1,000.00 ✅
- Risk per trade: 5.0% ✅
- All 3 pairs analyzed ✅
- Proper RSI values (0-100) ✅

**Pass/Fail:** ___________

**Notes:**
_______________________________________________________

---

## 🧪 Test 4: Configuration Changes

**Test 1: Change RSI Oversold**

```bash
nano config.yaml
# Change: rsi_oversold: 30 → rsi_oversold: 20
# Save and exit
python forex_test.py
```

**Expected Results:**
- ✅ Bot uses new RSI value (20)
- ✅ No code changes needed
- ✅ Configuration-driven behavior confirmed

**Test 2: Change Capital**

```bash
nano config.yaml
# Change: starting_capital: 1000.0 → starting_capital: 5000.0
# Save and exit
python forex_test.py
```

**Expected Results:**
- ✅ Bot uses new capital ($5,000)
- ✅ Trade sizes adjusted (5% of $5,000 = $250)

**Test 3: Reset to defaults**

```bash
nano config.yaml
# Change back to: rsi_oversold: 30, starting_capital: 1000.0
# Save and exit
```

**Pass/Fail:** ___________

**Notes:**
_______________________________________________________

---

## 🧪 Test 5: Error Handling

**Test 1: Invalid Config**

```bash
# Backup config
cp config.yaml config_backup.yaml

# Break the config
nano config.yaml
# Delete a required line (like rsi_period: 14)
# Save and exit

python forex_test.py
```

**Expected Results:**
- ✅ Validation fails
- ✅ Error message shows missing config
- ✅ Bot exits gracefully (doesn't crash)

**Restore config:**
```bash
cp config_backup.yaml config.yaml
rm config_backup.yaml
```

**Test 2: Network Simulation**

Run test, then:
1. Start the bot: `python forex_test.py`
2. Wait 10 seconds
3. Disconnect WiFi briefly
4. Reconnect WiFi

**Expected Results:**
- ✅ Retry logic kicks in
- ✅ "Retrying in 5 seconds..." message appears
- ✅ Bot recovers after reconnection
- ✅ Continues with other pairs if one fails

**Pass/Fail:** ___________

**Notes:**
_______________________________________________________

---

## 🧪 Test 6: Logging System

**Test 1: Console Output**

```bash
python forex_test.py
```

**Expected Results:**
- ✅ Clean, readable console output
- ✅ INFO level messages displayed
- ✅ Emojis render properly
- ✅ No excessive debug spam in console

**Test 2: Log File Details**

```bash
cat logs/bot_*.log | grep "DEBUG"
```

**Expected Results:**
- ✅ Detailed DEBUG messages in file
- ✅ API calls logged
- ✅ RSI calculations logged
- ✅ Every decision tracked

**Test 3: Error Tracking**

```bash
cat logs/bot_*.log | grep "ERROR"
```

**Expected Results:**
- ✅ Any errors are logged with details
- ✅ Timestamps included
- ✅ Context provided

**Pass/Fail:** ___________

**Notes:**
_______________________________________________________

---

## 🧪 Test 7: Multiple Runs

**Run the bot 3 times in a row:**

```bash
python forex_test.py
# Wait for completion
python forex_test.py
# Wait for completion
python forex_test.py
```

**Expected Results:**
- ✅ All 3 runs complete successfully
- ✅ Each creates a new log file
- ✅ No memory leaks
- ✅ Consistent behavior
- ✅ No interference between runs

**Check log files:**
```bash
ls -la logs/
```

**Expected:**
- ✅ Multiple log files with timestamps
- ✅ Each file ~10-50 KB

**Pass/Fail:** ___________

**Notes:**
_______________________________________________________

---

## 🧪 Test 8: Code Quality Check

**Check for:**

1. **No hardcoded values in Python files**
```bash
grep -n "1000.0" forex_test.py
grep -n "RSI_PERIOD = 14" forex_test.py
```

**Expected:** Should only find them as variables loaded from config

2. **All imports working**
```bash
python -c "from config_loader import Config; print('✅ Config import OK')"
python -c "from logger_config import setup_logger; print('✅ Logger import OK')"
```

**Expected:** Both print success messages

3. **No syntax errors**
```bash
python -m py_compile forex_test.py
python -m py_compile config_loader.py
python -m py_compile logger_config.py
```

**Expected:** No output = no errors

**Pass/Fail:** ___________

**Notes:**
_______________________________________________________

---

## 🧪 Test 9: Git Repository Health

**Check Git status:**

```bash
git status
```

**Expected Results:**
- ✅ Working tree clean (nothing uncommitted)
- ✅ No untracked important files
- ✅ logs/ directory ignored

**Check commit history:**

```bash
git log --oneline -10
```

**Expected Results:**
- ✅ Clear, descriptive commit messages
- ✅ Logical progression (Day 1 → Day 5)
- ✅ Professional formatting

**Check remote:**

```bash
git remote -v
```

**Expected Results:**
- ✅ Points to correct GitHub repo
- ✅ Both fetch and push configured

**Pass/Fail:** ___________

**Notes:**
_______________________________________________________

---

## 🧪 Test 10: GitHub Presentation

**Visit:** https://github.com/ethvoltrader/forex-trading-bot

**Check:**
- [ ] README renders correctly with formatting
- [ ] Badges display properly (Python, License, Status)
- [ ] Table of contents links work
- [ ] Code blocks have syntax highlighting
- [ ] All files present (8 files)
- [ ] No sensitive data visible (API keys, secrets)
- [ ] Recent commit visible
- [ ] Professional project description
- [ ] requirements.txt present

**Pass/Fail:** ___________

**Notes:**
_______________________________________________________

---

## 📊 Final Test Results Summary

| Test | Status | Notes |
|------|--------|-------|
| 1. Configuration System | ⬜ Pass / ⬜ Fail | |
| 2. Logger System | ⬜ Pass / ⬜ Fail | |
| 3. Full Bot Test | ⬜ Pass / ⬜ Fail | |
| 4. Configuration Changes | ⬜ Pass / ⬜ Fail | |
| 5. Error Handling | ⬜ Pass / ⬜ Fail | |
| 6. Logging System | ⬜ Pass / ⬜ Fail | |
| 7. Multiple Runs | ⬜ Pass / ⬜ Fail | |
| 8. Code Quality | ⬜ Pass / ⬜ Fail | |
| 9. Git Health | ⬜ Pass / ⬜ Fail | |
| 10. GitHub Presentation | ⬜ Pass / ⬜ Fail | |

**Overall Status:** ___________

---

## 🐛 Issues Found

List any issues discovered during testing:

1. _______________________________________________________
2. _______________________________________________________
3. _______________________________________________________

---

## ✅ Sign-Off

**Tested by:** ethvoltrader  
**Date:** _____________  
**Version:** Week 1 - Day 6  
**Status:** ⬜ Ready for Production / ⬜ Needs fixes

---

## 🚀 Next Steps

After all tests pass:
- [ ] Commit testing checklist to Git
- [ ] Proceed to Day 7 (Week Review)
- [ ] Celebrate Week 1 completion! 🎉

