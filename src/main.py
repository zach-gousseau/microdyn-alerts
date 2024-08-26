import argparse
from update_finder import UpdateFinder

def main():
    parser = argparse.ArgumentParser(description="Process email recipients, number of days, and db path")
    parser.add_argument(
        '--emails', 
        nargs='+', 
        required=True, 
        help="List of email recipients separated by space"
    )
    parser.add_argument(
        '--n_days', 
        type=int, 
        default=2, 
        help="Number of lookback days (default is 2)"
    )
    parser.add_argument(
        '--db_path', 
        type=str, 
        required=True, 
        help="Path to the SQLite database"
    )
    
    # parse arguments
    args = parser.parse_args()
    email_recipients = args.emails
    n_days = args.n_days
    db_path = args.db_path

    # initialize
    update_finder = UpdateFinder(
        n_days=n_days, 
        db_path=db_path, 
        email_recipients=email_recipients
    )

    # run it.
    update_finder.run()

if __name__ == "__main__":
    main()
