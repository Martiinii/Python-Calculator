import expr

while True:
    i = input()
    try:
        print(f'{expr.Expression(i).calculate()}\n')
    except OverflowError as e:
        print('Result too big!\n')
    except Exception as e:
        print(f'{e}\n')