Table of Contents
- The Strategy
- Prerequisites
- Starting the Application
- Closing the Application
- Parameters
- Running Multiple Currencies and/or Strategies
__________________________________________________________________________________
### The Strategy
The application uses a voting system of RSIs and Bollinger Bands. These functions are explained more in the 'Parameters' section below.

RSI: If the RSI passes the RSI overbought threshold, there is a vote to SELL. If the RSI passes the oversold threshold, there is a vote to BUY.

Bollinger Bands: If the latest close passes the upper Bollinger Band, there is a vote to SELL. If the latest close passes the lower Bollinger Band, there is a vote to BUY.

##### BUY Criteria: The algorithm will trigger a buy order only when all of the following conditions are met:
	1. There is 'Trade Currency' in the account.
	2. RSI votes BUY.
	3. Bollinger Bands vote BUY.

##### SELL Criteria: The algorithm will trigger a sell order only when all of the following conditions are met:
	1. There is 'Coin Symbol' in the account.
	2. RSI votes SELL.
	3. Bollinger Bands vote SELL.
	4. The curent close is higher than the maximum bought price and still 	profitable after accounting for the 1% Exchange fees from Gemini (this 	ensures you do not lose money on a sell).

All BUY and SELL orders are 'immediate or cancel'.

### PREREQUISITES
	You will need an API Key and API Sectret from Gemini Exchange. This allows the 	application to  communicate with the Gemini Exchange and Market. You can easily 	obtain one of these from https://www.gemini.com/ under Account -> Settings -> API.
Please also ensure you have funds in your Gemini account that correspond to the Trade Currency you have selected (see 'Parameters').

### STARTING THE APPLICATION
	When you start this application, a blank terminal will appear. Please allow for up to 15 seconds for the application interface to appear as well.
	Once you have entered in the appropriate parameters (see below), hit 'Confirm and run'. This will start the algorithm. You will see the progress of each close reported on the terminal.

### CLOSING THE APPLICATION
	To close the application, please click the 'X' on the top right of the terminal. This will end th algorithm and you will no longer be watching the market to BUY or SELL.

### PARAMETERS
##### Sandbox vs Live
This is the environment you will run your code in. You can sign up for a sandbox accouunt with Gemini at https://exchange.sandbox.gemini.com/ in order to test the application in a sandbox environment (paper-trading) before running on your Live account with real money and trades. This will require a sandbox API Key and API Secret, which are acquired from the sandbox exchange in the same way detailed above under 'Prerequisites'.

##### Coin Symbol
This is the symbol you would like to trade for - when you BUY, you are buying this currency. When you SELL, you are selling this currency.

##### Trade Currency
This is the currency you are trading with. When you BUY, you are paying with this currency. When you sell, you are receiving this currency. Please ensure this is a valid Coin Symbol and Trade Currency combination.

##### Candle Length
This is the length of each period as it relates to RSI and Bollinger Bands. The application will receive the close price at the end of each period and use it to calculate BUY and SELL criteria. The length of the candle will partly determine your trade strategy. Use a longer length for a more long term strategy, and a shorter length to constantly check the market for quick BUY and SELL opportunities. The options are:

1m - 1 minute

5m - 5 minutes

15m - 15 minutes

30m - 30 minutes

1hr - 1 hour

6hr - 6 hours

1d - 1 day

##### RSI Periods
This determines the amount of periods (closes calculated at the interval determined by Candle Length) used to determine the RSI (Relative Strength Index). You can learn about RSIs here: https://www.investopedia.com/terms/r/rsi.asp. The default is 14.

##### RSI Overbought Threshold
This is the threshold to determine when a cryptocurrency is overbought and should be sold. The default is 70.

##### RSI Oversold Threshold
This is the threshold to determine when a cryptocurrency is oversold and should be bought. The default is 30.

##### Bollinger Bands Periods
This determines the amount of periods (closes calculated at the interval determined by Candle Length) used to determine the Bollinger Bands for the closes. You can learn about Bollinger Bands here: https://www.investopedia.com/terms/b/bollingerbands.asp. The default is 14.

##### Band Standard Deviations
This is the amount of standard deviations used to determine the Bollinger Bands based off of the rolling average of closes for the amount of periods set with the 'Bollinger Bands Periods' perameter. The default is 1.5.

##### Unique Instance
This is an instance identifier used so that you may run the application with multiple currencies and/or strategies at once. If you only plan to run one currency at a time, this field does not matter. Otherwise, please see the 'Running Multiple Currencies and/or Strategies' section below.

##### Your Gemini API Key
This is where you enter your Gemini API Key. Please ensure you are using the right Key for the environment you have selected. Please see the 'Prerequisites' section above if you do not have a Gemini API Key.

##### Your Gemini API Secret
This is where you enter your Gemini API Secret. Please ensure you are using the right Secret for the environment you have selected. Please see the 'Prerequisites' section above if you do not have a Gemini API Secret.

### RUNNING MULTIPLE CURRENCIES AND/OR STRATEGIES
In order to run multiple currencies and/or strategies at once, you must open separate instances of the application. For each, select the parameters you wish to use - these can be different Coin Symbol and Trade Currency pairings, different RSI and Bollinger Bands parameters, or both. MAKE SURE YOU SELECT A DIFFERENT 'UNIQUE INSTANCE' FOR EACH. Otherwise, you will receive an error. Once the parameters are filled on the new instance, hit 'Confirm and run'. You will see the progress of each close reported on the terminal for the new instance. This will not interfer with any other instance(s) (as long as you have selected a different 'Unique Identifier').
