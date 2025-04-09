# CS50 Finance

CS50 Finance is a web application that allows users to manage their stock portfolio. Built as part of Harvard University's CS50 course, this project provides a platform for users to buy and sell stocks, view their portfolio, and track stock prices in real-time.

## Features

- **User  Authentication**: Secure login and registration for users.
- **Stock Trading**: Buy and sell stocks with real-time price updates.
- **Portfolio Management**: View current holdings and their values.
- **Stock Lookup**: Search for stocks and view their current prices and historical data.
- **Transaction History**: Keep track of all transactions made by the user.

## Technologies Used

- **Languages**: Python, HTML, CSS, JavaScript
- **Frameworks**: Flask
- **Database**: SQLite
- **APIs**: IEX Cloud for real-time stock data

## Installation

To set up the project locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/Sufail07/CS50-Finance.git
   cd CS50-Finance
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```bash
   python create_db.py
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your web browser and navigate to `http://127.0.0.1:5000`.

## Usage

1. **Register**: Create a new account by providing a username and password.
2. **Login**: Use your credentials to log in to your account.
3. **Buy Stocks**: Use the "Buy" feature to purchase stocks by entering the stock symbol and the number of shares.
4. **Sell Stocks**: Use the "Sell" feature to sell your stocks.
5. **View Portfolio**: Check your current holdings and their values in the portfolio section.
6. **Search Stocks**: Use the search feature to find stock information.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgments

- Harvard University CS50 course for providing the foundation for this project.
- IEX Cloud for providing stock market data.

## Contact

For any questions or feedback, please reach out to [Sufail07](https://github.com/Sufail07).

---

Feel free to modify this README to better fit your project's specifics or to add any additional information that may be relevant!
