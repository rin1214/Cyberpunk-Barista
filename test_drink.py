from drink import Drink


# Create a new drink
drink = Drink()


# --------------------------------------------------
# TEST 1: STARTING VALUES
# --------------------------------------------------

print("STARTING DRINK")
print(drink)


# --------------------------------------------------
# TEST 2: INCREASE SWEETNESS
# --------------------------------------------------

print("\nINCREASING SWEETNESS")

drink.increase_sweetness()

print(drink)


# --------------------------------------------------
# TEST 3: DECREASE CAFFEINE
# --------------------------------------------------

print("\nDECREASING CAFFEINE")

drink.decrease_caffeine()

print(drink)


# --------------------------------------------------
# TEST 4: INCREASE TEMPERATURE TWICE
# --------------------------------------------------

print("\nINCREASING TEMPERATURE")

drink.increase_temperature()
drink.increase_temperature()

print(drink)


# --------------------------------------------------
# TEST 5: SHOW DRINK DATA
# --------------------------------------------------

print("\nDRINK DATA")

print(drink.get_data())



# --------------------------------------------------
# TEST 6: RESET THE DRINK
# --------------------------------------------------

print("\nRESETTING DRINK")

drink.reset()

print(drink)


# --------------------------------------------------
# TEST 7: MAXIMUM SAFETY LIMIT
# --------------------------------------------------

print("\nTESTING MAXIMUM LIMIT")

drink.reset()

for _ in range(15):
    drink.increase_sweetness()

print("Sweetness should stop at 100:")
print(drink)


# --------------------------------------------------
# TEST 8: MINIMUM SAFETY LIMIT
# --------------------------------------------------

print("\nTESTING MINIMUM LIMIT")

drink.reset()

for _ in range(15):
    drink.decrease_caffeine()

print("Caffeine should stop at 0:")
print(drink)