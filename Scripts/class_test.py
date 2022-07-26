class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def print_age(self):
        print(f'Age is {self.age} and my name is {self.name}')

class Student(Person):
  def __init__(self, fname, lname, year):
    super().__init__(fname, lname)
    self.graduationyear = year

  def welcome(self):
    print("Welcome", self.name, 'age', self.age, "to the class of", self.graduationyear)

p1 = Person("John", 36)

print(p1.name)
print(p1.age)
p1.print_age()


studio = Student('Harold', 23, 2017)
studio.welcome()