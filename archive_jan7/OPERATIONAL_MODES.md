# Stock Intelligence Copilot - Operational Modes

## 🟢 Production Mode (SEBI-Compliant)

**Status**: Always available, default mode

**Features**:
- ✅ READ-ONLY context layer (MCP)
- ✅ Technical analysis signals
- ✅ Fundamental data integration
- ✅ Portfolio tracking
- ✅ Risk assessment
- ✅ Proper disclaimers
- ✅ SEBI-compliant language

**Configuration**: `backend/.env`
```bash
MCP_ENABLED=true
```

---

## 🟡 Experimental Mode (Personal Use Only)

**Status**: DISABLED by default

**⚠️ WARNING**:
- NOT compliant with SEBI regulations
- Generates predictions (can be wrong)
- Uses direct/aggressive language
- User assumes ALL responsibility
- For personal experimentation only
- NOT for public use or distribution

**Features**:
- Price range predictions
- Trade bias suggestions (long/short/no_trade)
- Regime detection
- Invalidation levels
- Probabilistic reasoning
- Blunt risk assessment

**Configuration**: `backend/.env.experimental`
```bash
EXPERIMENTAL_AGENT_ENABLED=true
EXPERIMENTAL_RISK_ACKNOWLEDGED=true
```

**How to Enable**:

1. Copy settings from `.env.experimental` to `.env`
2. Set `EXPERIMENTAL_AGENT_ENABLED=true`
3. Set `EXPERIMENTAL_RISK_ACKNOWLEDGED=true`
4. Restart backend

**Usage Example**:
```python
from app.core.experimental.trading_agent import ExperimentalTradingAgent

# Initialize (disabled by default)
agent = ExperimentalTradingAgent(enabled=True)

# Generate thesis
thesis = agent.analyze_setup(
    ticker="RELIANCE.NS",
    current_price=2850.0,
    ohlcv={...},
    indicators={...}
)

# Display result
print(format_experimental_output(thesis))
```

---

## 🔀 Mode Comparison

| Feature | Production Mode | Experimental Mode |
|---------|----------------|-------------------|
| **Compliance** | ✅ SEBI-compliant | ❌ Not compliant |
| **Language** | Conservative | Aggressive |
| **Predictions** | ❌ No | ✅ Yes |
| **Trade Suggestions** | ❌ No | ✅ Yes |
| **Disclaimers** | ✅ Required | ⚠️ User responsibility |
| **Public Use** | ✅ Yes | ❌ Personal only |
| **Default Status** | ✅ Enabled | ❌ Disabled |

---

## 📋 Recommended Workflow

### For General Use (Recommended)
```
1. Use Production Mode
2. Get signals with context
3. Make your own decisions
4. Stay compliant
```

### For Personal Experimentation
```
1. Understand the risks
2. Enable Experimental Mode
3. Review all outputs critically
4. Keep detailed logs
5. Never share outputs publicly
6. Disable when not actively testing
```

---

## 🚨 Important Disclaimers

### Production Mode
> This system provides informational signals based on technical analysis. It is not financial advice. All investment decisions carry risk. Past performance does not guarantee future results. Consult a registered financial advisor before making investment decisions.

### Experimental Mode
> ⚠️ **EXPERIMENTAL - PERSONAL USE ONLY**
>
> This experimental agent generates tactical trading hypotheses for personal learning and experimentation. It:
> - Can and WILL be wrong
> - Is NOT compliant with SEBI regulations
> - Does NOT constitute financial advice
> - Should NOT be shared publicly
> - Assumes user has full knowledge of risks
>
> **USER ASSUMES ALL RESPONSIBILITY**

---

## 🛡️ Safety Features

Both modes include:
- ✅ Comprehensive logging
- ✅ Audit trails
- ✅ Error handling
- ✅ No automatic trade execution
- ✅ User confirmation required

Experimental mode adds:
- ✅ Explicit risk acknowledgment requirement
- ✅ Disabled by default
- ✅ Separate codebase
- ✅ Clear visual warnings

---

## 📞 Support

For questions or issues:
- Production Mode: Standard support
- Experimental Mode: Self-service only (personal responsibility)

---

**Remember**: The experimental mode is a learning tool, not a trading system. Always do your own research and maintain proper risk management.
