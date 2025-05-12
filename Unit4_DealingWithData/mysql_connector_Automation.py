import mysql.connector
from typing import List, Tuple, Any, Optional, Union, Dict
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Configuration for database connection"""
    host: str = 'localhost'
    user: str = 'root'
    password: str = 'Password'
    database: str = 'your_database'


class SQLHelper:
    """
    A flexible SQL helper class that can work with any database and any SQL query.
    This class provides methods to execute any SQL operation and handle the results.
    """

    def __init__(self, config: DatabaseConfig):
        """Initialize the SQL helper with database configuration"""
        self.config = config
        self.connection = None
        self.cursor = None

    def connect(self) -> None:
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config.host,
                user=self.config.user,
                password=self.config.password,
                database=self.config.database
            )
            self.cursor = self.connection.cursor(buffered=True)
            print("Successfully connected to the database!")
        except mysql.connector.Error as err:
            print(f"Error connecting to database: {err}")
            raise

    def disconnect(self) -> None:
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

    def execute_query(self, query: str, values: Optional[Tuple] = None) -> List[Tuple]:
        """
        Execute any SQL query and return results
        Args:
            query: The SQL query to execute
            values: Optional tuple of values for parameterized queries
        Returns:
            List of tuples containing the query results
        """
        try:
            self.cursor.execute(query, values or ())
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
            raise

    def execute_many(self, query: str, values: List[Tuple]) -> int:
        """
        Execute a query multiple times with different values
        Args:
            query: The SQL query to execute
            values: List of tuples containing values for each execution
        Returns:
            Number of affected rows
        """
        try:
            self.cursor.executemany(query, values)
            self.connection.commit()
            return self.cursor.rowcount
        except mysql.connector.Error as err:
            print(f"Error executing multiple queries: {err}")
            self.connection.rollback()
            raise

    def execute_script(self, script: str) -> None:
        """
        Execute a SQL script containing multiple statements
        Args:
            script: The SQL script to execute
        """
        try:
            for result in self.connection.cursor().execute(script, multi=True):
                if result.with_rows:
                    print(f"Rows produced by statement: {result.fetchall()}")
                else:
                    print(f"Number of rows affected by statement: {result.rowcount}")
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Error executing script: {err}")
            self.connection.rollback()
            raise

    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get information about a table's columns
        Args:
            table_name: Name of the table to get information about
        Returns:
            List of dictionaries containing column information
        """
        try:
            self.cursor.execute(f"DESCRIBE {table_name}")
            columns = self.cursor.fetchall()
            return [{
                'field': col[0],
                'type': col[1],
                'null': col[2],
                'key': col[3],
                'default': col[4],
                'extra': col[5]
            } for col in columns]
        except mysql.connector.Error as err:
            print(f"Error getting table info: {err}")
            raise


def main():
    # Example usage
    print("Welcome to the SQL Helper!")
    print("Please enter your database configuration:")

    # Get database configuration from user
    host = input("Host (default: localhost): ") or 'localhost'
    user = input("Username (default: root): ") or 'root'
    password = input("Password: ")
    database = input("Database name: ")

    # Initialize configuration
    config = DatabaseConfig(
        host=host,
        user=user,
        password=password,
        database=database
    )

    # Create SQL helper instance
    sql = SQLHelper(config)

    try:
        # Connect to database
        sql.connect()

        while True:
            print("\nWhat would you like to do?")
            print("1. Execute a single query")
            print("2. Execute multiple queries")
            print("3. Execute a SQL script")
            print("4. Get table information")
            print("5. Exit")

            choice = input("Enter your choice (1-5): ")

            if choice == '1':
                query = input("\nEnter your SQL query: ")
                values_input = input("Enter values (comma-separated, or press Enter for none): ")
                values = tuple(values_input.split(',')) if values_input else None

                try:
                    results = sql.execute_query(query, values)
                    print("\nResults:")
                    for row in results:
                        print(row)
                except Exception as e:
                    print(f"Error: {e}")

            elif choice == '2':
                query = input("\nEnter your SQL query: ")
                num_values = int(input("How many sets of values do you want to execute? "))
                values = []

                for i in range(num_values):
                    value_input = input(f"Enter values for set {i + 1} (comma-separated): ")
                    values.append(tuple(value_input.split(',')))

                try:
                    affected_rows = sql.execute_many(query, values)
                    print(f"\nSuccessfully executed {affected_rows} rows")
                except Exception as e:
                    print(f"Error: {e}")

            elif choice == '3':
                print("\nEnter your SQL script (press Enter twice to finish):")
                script_lines = []
                while True:
                    line = input()
                    if not line:
                        break
                    script_lines.append(line)

                try:
                    sql.execute_script('\n'.join(script_lines))
                    print("\nScript executed successfully")
                except Exception as e:
                    print(f"Error: {e}")

            elif choice == '4':
                table_name = input("\nEnter table name: ")
                try:
                    table_info = sql.get_table_info(table_name)
                    print("\nTable Information:")
                    for col in table_info:
                        print(f"Column: {col['field']}, Type: {col['type']}, Null: {col['null']}")
                except Exception as e:
                    print(f"Error: {e}")

            elif choice == '5':
                print("Goodbye!")
                break

            else:
                print("Invalid choice. Please try again.")

    finally:
        # Always disconnect
        sql.disconnect()


if __name__ == "__main__":
    main()


# === Future Improvements ===
# - Add query history or logging to a .log file
# - Add EXPLAIN plan option for advanced users
# - Save/load common queries from a config JSON/YAML
# - Add retry logic for connection loss
# - Add A opensource model that work for prompts SQL
