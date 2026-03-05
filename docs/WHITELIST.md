# 🔒 Whitelist Configuration Guide

## How to Control Who Can Create Tickets

### Option 1: Allow ALL Numbers (Default)

Edit `config/whitelist.json`:
```json
{
  "allowed_numbers": [],
  "description": "Empty array = allow all numbers"
}
```

### Option 2: Restrict to Specific Numbers

Edit `config/whitelist.json`:
```json
{
  "allowed_numbers": [
    "923351244708",
    "923330220803",
    "1234567890"
  ],
  "description": "Only these numbers can create tickets"
}
```

**Format Rules:**
- ✅ Numbers WITHOUT + sign
- ✅ Numbers WITHOUT spaces
- ✅ Just digits: `923351244708`
- ❌ NOT like: `+92 335 1244708`
- ❌ NOT like: `+923351244708`

### How to Find a Number:

When someone messages the bot, check the console:
```
📨 Message from Dr. Nausheen (923351244708):
```

The number is: `923351244708` - copy this exact format!

### After Changing Whitelist:

**MUST restart the bot:**
```bash
# Stop bot (Ctrl+C)
# Start again
./start.sh
```

The bot will show:
```
✅ Loaded 2 whitelisted numbers
🔒 Whitelist ENABLED - only these numbers can create tickets:
   • 923351244708
   • 923330220803
```

### Testing:

1. **Allowed number** sends message → Creates ticket ✅
2. **Blocked number** sends message → Gets "not authorized" message ❌

### Quick Commands:

**Allow everyone:**
```bash
echo '{"allowed_numbers":[]}' > config/whitelist.json
```

**Allow specific numbers:**
```bash
cat > config/whitelist.json << 'EOF'
{
  "allowed_numbers": [
    "923351244708",
    "923052294590"
  ]
}
EOF
```

Then restart: `./start.sh`

---

**Note:** Numbers are automatically cleaned (+ and spaces removed) so minor format differences work!
