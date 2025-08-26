# ZKsync Farmer Bot V2

This is a follow up to my [ZKsync V1](https://github.com/KichdiPatel/zksync-airdrop-farmer-v1). This was an update built in python storing the data in a postgreSQL database. 

The goal of this project was to build a airdrop farmer for the ZKsync airdrop across multiple wallets passively. It was build in 2023, when I was beginning coding projects, but I am now opensourcing it. 

In the database, the wallets, and the queue were being stored. I had designed a simple queue that would run within the postgreSQL DB. So, everytime changes are made, the database is sorted. This makes it easy for running the next transaction for a particular wallet since queue would store information like time to run transaction, wallet to run transaction, protocol, type of transaction, etc. 

Wallets.py and DataQueue.py define the models for storing the important data. The rest of the project files are used for transaction handling logic. ABIs that I used for this project are also stored in the ABI folder. 

This project simplifies logic used in V1, stores everything in a database, and uses Python. There is more to it, but it was a very interesting project to work on. 

I didn't end up getting the airdrop, but learned a lot which helped me create a profitable [Aevo Airdrop Bot](https://github.com/KichdiPatel/aevo-airdrop-farmer). 

