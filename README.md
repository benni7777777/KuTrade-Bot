# KuTrade Bot 🚀

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Trading](https://img.shields.io/badge/Trading-High%20Risk-red)

An automated cryptocurrency trading bot for KuCoin Futures markets that generates trading signals, executes trades, and manages positions automatically.

## ⚠️ IMPORTANT DISCLAIMER

**USE THIS SOFTWARE AT YOUR OWN RISK. TRADING CRYPTOCURRENCIES IS EXTREMELY RISKY.**

By using this software, you understand and agree that:

1. Cryptocurrency trading involves substantial risk of loss and is not suitable for all investors
2. Past performance is not indicative of future results
3. This bot is provided strictly as open-source software, with NO GUARANTEES of:
   - Profit or income
   - Fitness for any particular purpose
   - Accuracy of trading signals
   - Protection against financial losses

4. The creator(s) and contributors:
   - Accept NO RESPONSIBILITY for your trading results
   - Are NOT financial advisors
   - Make NO CLAIMS about trading performance
   - Cannot and will not provide trading advice

5. You are strongly advised to:
   - Never trade with money you cannot afford to lose
   - Start with small amounts to test the system
   - Understand all risks involved
   - Consult with licensed financial advisors before trading

### Why Open Source?

This project is open-sourced under the MIT license because:
1. We believe in transparency and community-driven development
2. Trading algorithms should be open for inspection and improvement
3. Educational purposes - to help others learn about algorithmic trading
4. Commitment to the open-source philosophy of sharing knowledge

**Remember:** Just because this code is open source doesn't mean it's risk-free. Always do your own research and testing.

## 🙏 Special Thanks

Special thanks to the [Cline project](https://github.com/cline/cline) for their groundbreaking work in AI-assisted development. Their open-source contributions and innovative approach to autonomous coding agents have been instrumental in shaping the development of KuTrade Bot.

## 🚨 Important Notice

This is a trading bot that deals with real money and cryptocurrencies. While efforts have been made to ensure its reliability, please note:
- This is for educational purposes
- Test thoroughly with small amounts first
- Past performance does not guarantee future results
- Never risk money you cannot afford to lose

## ✨ Features

- Automated trading signal generation
- Real-time trade execution
- Position management and profit taking
- Configurable trading parameters
- Secure API handling
- Error recovery and logging

## Overview

This trading bot is designed to:
1. Generate trading signals based on market analysis
2. Execute trades on KuCoin Futures
3. Manage positions and take profits
4. Run in automated cycles

## Project Structure

- `GO.PY` - Main orchestrator script that manages the trading cycle
- `1.py` - Signal generation and market analysis
- `2.py` - Trade execution based on generated signals
- `close.py` - Position management and profit-taking
- `delete.py` - Utility script for cleanup operations
- `main.py` - Additional utility functions
- `.env` - Configuration file for KuCoin API credentials

## Prerequisites

- Python 3.8 or higher
- KuCoin Futures account
- API credentials from KuCoin (API Key, Secret, and Passphrase)

## Installation

1. Clone this repository
2. Install required packages:
```bash
pip install -r requirements.txt
```
3. Create a `.env` file with your KuCoin credentials:
```
KUCOIN_KEY=your_api_key
KUCOIN_SECRET=your_api_secret
KUCOIN_PASSPHRASE=your_passphrase
```

## Usage

1. Start the bot by running:
```bash
python GO.PY
```
2. Enter the number of hours you want the bot to run
3. The bot will then:
   - Generate signals every 45 minutes
   - Execute trades based on those signals
   - Manage positions and take profits
   - Repeat the cycle

## Trading Cycle

1. Signal Generation (1.py):
   - Analyzes market data
   - Generates trading signals
   - Waits 30 seconds for signal confirmation

2. Trade Execution (2.py):
   - Places trades based on generated signals
   - Implements position sizing and risk management

3. Position Management (close.py):
   - Monitors open positions
   - Takes profits when targets are reached
   - Manages stop losses

4. Cycle Completion:
   - Waits 45 minutes for trades to develop
   - Prepares for the next cycle

## Security

- API credentials are stored securely in the `.env` file
- Uses KuCoin API v2 authentication
- Implements secure request signing

## Error Handling

- Automatic retry mechanism for API failures
- 5-minute cooldown on errors
- Comprehensive error logging

## Important Notes

1. Always test with small amounts first
2. Monitor the bot regularly
3. Keep your API credentials secure
4. Ensure stable internet connection
5. Keep enough funds in your account for trading

## Disclaimer

Trading cryptocurrencies carries significant risk. This bot is provided as-is with no guarantees. Always understand the risks involved and never trade with money you cannot afford to lose. 

## 🔧 Configuration

The bot uses the following environment variables in the `.env` file:
```env
KUCOIN_KEY=your_api_key
KUCOIN_SECRET=your_api_secret
KUCOIN_PASSPHRASE=your_passphrase
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⭐ Support

If you found this project helpful, please consider giving it a star on GitHub!

## 📧 Contact

If you have any questions or suggestions, feel free to open an issue on GitHub. 