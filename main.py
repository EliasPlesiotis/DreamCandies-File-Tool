import sys
import io

class ErrorHandler:
    def __init__(self, out: io.FileIO = sys.stdout):
        self.out = out

    def __call__(self, func):
        def _wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception as e:
                self.out.write(f'Error: {e}')
                self.out.write(f'\nUsage:')
                self.out.write(f'\n\tArgumemt --sampe: the sample csv')
                self.out.write(f'\n\tArgumemt --files-location: location of the folder with CUSTOMER.csv, INVOICE.csv, INVOICE_ITEM.csv')
                self.out.write('\n')
                self.out.write(f'\nExample: python main.py --sample ./sample.csv --files-location ../db_export')
        return _wrapper

def parse_args(args):
    args = { k.replace('--', ''):v for k, v in zip(args[1::2], args[2::2]) }
    assert list(args.keys()) == ['sample', 'files-location'], 'Use --sample and --files-location as arguments'
    return args

class Customer:
    def __init__(self, customer_code, first_name = None, last_name = None):
        self.__customer_code = customer_code
        self.__first_name = first_name
        self.__last_name = last_name

    def __init__(self, *args):
        self.__customer_code, self.__first_name, self.__last_name = args

    def __eq__(self, c):
        return c.__customer_code == self.__customer_code
    
    def __str__(self):
        return f'{self.__customer_code} {self.__first_name} {self.__last_name}'

    def get_customer_code(self): return self.__customer_code

class Invoice:
    def __init__(self, customer_code, invoice_code = None, amount = None, date = None):
        self.__customer_code = customer_code
        self.__invoice_code = invoice_code
        self.__amount = amount
        self.__date = date

    def __init__(self, *args):
        self.__customer_code, self.__invoice_code, self.__amount, self.__date = args

    def __eq__(self, inv):
        return self.__customer_code == inv.__customer_code

    def __str__(self):
        return f'{self.__customer_code} {self.__invoice_code} {self.__amount} {self.__date}'

    def get_invoice_code(self):
        return self.__invoice_code

class Item:
    def __init__(self, invoice_code, item_code, amount, quantity):
        self.__invoice_code = invoice_code
        self.__item_code = item_code
        self.__amount = amount
        self.__quantity = quantity
    
    def __init__(self, *args):
        self.__invoice_code, self.__item_code, self.__amount, self.__quantity = args

    def __eq__(self, it):
        return self.__invoice_code == it.__invoice_code

    def __str__(self):
        return f'{self.__invoice_code} {self.__item_code} {self.__amount} {self.__quantity}'

@ErrorHandler()
def main():
    version = sys.version_info
    if version.major != 3 and version.minor != 9:
        raise 'Python 3.9 is required'
    
    args = parse_args(sys.argv)

    CUSTOMER_CSV = 'CUSTOMER.csv'
    INVOICE_ITEM_CSV = 'INVOICE_ITEM.csv'
    INVOICE_CSV = 'INVOICE.csv'

    customers = []
    invoices = []
    invoice_items = []

    if args['files-location'][-1] != '/':
        args['files-location'] = args['files-location'] + '/'

    with open(args['sample']) as sample_file, open(args['files-location'] + CUSTOMER_CSV) as customer_csv, open(args['files-location'] + INVOICE_CSV) as invoice_csv, open(args['files-location'] + INVOICE_ITEM_CSV) as invoice_item_csv:
        sample_file.readline()
        sample = [ Customer(line.rstrip(), None, None) for line in sample_file ]

        customer_headers = customer_csv.readline()
        while line := customer_csv.readline():
            c = Customer(*line.rstrip().split(','))
            if c in sample:
                customers.append(c)
                sample = [ cust for cust in filter(lambda x: not c == x, sample) ]
        
        temp_invoices = [ Invoice(c.get_customer_code(), None, None, None) for c in customers ]
        invoice_headers = invoice_csv.readline()
        while line := invoice_csv.readline():
            inv = Invoice(*line.rstrip().split(','))
            if inv in temp_invoices:
                invoices.append(inv)

        temp_items = [ Item(inv.get_invoice_code(), None, None, None) for inv in invoices ]
        items_headers = invoice_item_csv.readline()
        while line := invoice_item_csv.readline():
            item = Item(*line.rstrip().split(','))
            if item in temp_items:
                invoice_items.append(item)

    with open('./output_customer.csv', 'w') as o_customer_csv, open('./output_invoice.csv', 'w') as o_invoice_csv, open('./output_invoice_item.csv', 'w') as o_invoice_item:
        o_customer_csv.write(customer_headers + '\n'.join([ str(c) for c in customers ]))
        o_invoice_csv.write(invoice_headers + '\n'.join([ str(inv) for inv in invoices]))
        o_invoice_item.write(items_headers + '\n'.join([ str(inv_it) for inv_it in invoice_items]))
    
    print('Files created successfully in the current directory')

if __name__ == '__main__':
    main()