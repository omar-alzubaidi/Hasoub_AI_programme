class Car:
    def __init__(self, color, engine_displacement):
        #تعريف خصائص السيارة اللون, سعه المحرك والمسافه هنا المسافه تبدا من صفر لذلك لا داعي لاضافتها في self
        self.color = color
        self.engine_displacement = engine_displacement
        self.distance = 0

    def reset_counter(self):
        #تعريف العداد واعادته
        self.distance = 0

    def increase_counter(self, amount):

        if amount > 0:
            self.distance += amount
        else:
            print("Distance increment must be positive")

    def display_info(self):

        print(f"Color: {self.color}, Engine: {self.engine_displacement}, Distance: {self.distance}")


# Example Usage:
my_car = Car("Red", "2.0L")
my_car.display_info()

my_car.increase_counter(-100)
my_car.display_info()

my_car.reset_counter()
my_car.display_info()
