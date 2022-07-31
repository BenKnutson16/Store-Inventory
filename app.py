from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import csv
import datetime

engine = create_engine('sqlite:///inventory.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Product(Base):
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True)
    product_name = Column(String)
    product_quantity = Column(Integer)
    product_price = Column(Integer)
    date_updated = Column(DateTime)


def add_csv():
    with open("inventory.csv") as file:
        data = list(csv.DictReader(file))
        for row in data:
            name = row['product_name']
            quantity = int(row['product_quantity'])
            price = clean_price(row['product_price'])
            date = clean_date(row['date_updated'])
            new_product = Product(product_name=name, product_quantity=quantity,
                                  product_price=price, date_updated=date)
            session.add(new_product)
        session.commit()


def clean_price(price):
    cleaned_price = float(price.split('$')[1])
    return int(cleaned_price * 100)


def clean_date(date):
    split_date = date.split('/')
    return datetime.date(int(split_date[2]), int(split_date[0]), int(split_date[1]))


def menu():
    while True:
        selection = input('''\nMenu:
                        \rPlease enter an option:
                        \rV) View a single product's inventory
                        \rA) Add a new product to the database
                        \rB) Backup inventory to file
                        \rQ) Quit Program
                        \n''').lower()
        if selection == 'v':
            view_product()
        elif selection == 'a':
            add_product()
        elif selection == 'b':
            backup()
        elif selection == 'q':
            return
        else:
            print("Error. Please enter a single letter for the menu option you wish to select.")


def view_product():
    while True:
        product_num = input("Enter the id of the product you wish to view: ")
        view_query = session.query(Product).filter_by(product_id=product_num)
        if not view_query.one_or_none():
            print("Error: Invalid product ID. Please Try again. ")
        else:
            for item in view_query:
                print(f'''
                    \rProduct name: {item.product_name}
                    \rPrice: ${(item.product_price/100):.2f}
                    \rQuantity: {item.product_quantity}
                    \rDate Updated: {item.date_updated.strftime("%Y/%m/%d")}
                    ''')
            input("Press enter to return to menu")
            return


def add_product():
    name = input("Please enter name of new product: ")
    check = True
    while check:
        try:
            price = int(input("Please enter price in cents with no currency symbol: "))
            quantity = int(input("Please enter quantity: "))
        except ValueError:
            print("Error: Invalid price or quantity. Try again")
        else:
            check = False
    product_input = Product(product_name=name, product_price=price,
                            product_quantity=quantity, date_updated=datetime.datetime.now())
    duplicate = session.query(Product).filter_by(product_name=name).one_or_none()
    if duplicate:
        for item in session.query(Product).filter_by(product_name=name):
            existing_date = item.date_updated
        if product_input.date_updated >= existing_date:
            session.add(product_input)
            session.commit()
            print("Duplicate item found, item updated successfully.\n")
        else:
            print(f"The product '{name}' has already been added to the database.\n")
    else:
        session.add(product_input)
        session.commit()
        print("Product added successfully.\n")
    input("Press enter to return to menu")


def backup():
    with open("backup.csv", 'a', newline='') as csvfile:
        fieldnames = ['product_name', 'product_price', 'product_quantity', 'date_updated']
        backup_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        backup_writer.writeheader()
        for line in session.query(Product).order_by(Product.product_id):
            name = line.product_name
            price = f"${float(line.product_price)/100:.2f}"
            quantity = line.product_quantity
            date = line.date_updated.strftime("%m/%d/%Y")
            backup_writer.writerow({
                'product_name': name,
                'product_price': price,
                'product_quantity': quantity,
                'date_updated': date
            })


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    add_csv()
    menu()
