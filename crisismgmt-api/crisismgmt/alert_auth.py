import time
from threading import Thread

panic = True
userList = []
timerList = []

def add_user(user_id):
    if panic:
        userList.append(user_id)
        timerList.append(10) #Timer currently set to 10 seconds
    for i in range(len(timerList)):
        timerList[i]-=1
        time.sleep(1/len(timerList))
    print(timerList, userList)

# Testing purposes
add_user(4)
add_user(5)
add_user(6)

# Loop function detects if user has been on list for longer than 60 mins
def loop_function():
    while len(timerList) > 0:
        for i in range(len(timerList)):
            timerList[i] -= 1
            time.sleep(1/len(timerList))
        # print(timerList, userList)
        print("Timer list is {}".format(timerList), "User list is {}".format(userList))

        if timerList[0] == 0:
            timerList.remove(timerList[0])
            userList.remove(userList[0])

        if len(timerList) == 0:
            print("done")

background_thread = Thread(target=loop_function)
background_thread.start() # Have function run in background constantly


add_user(23) #Testing purposes
    