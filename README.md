# Budget Blocks DS API
[Web Front-end](https://www.budgetblocks.org/)

[DS API](https://api.budgetblocks.org/)

## Contributers

| Adriann Lefebvere | Christopher Jakuc |
|:--:|:--:|
| <img src="https://media-exp1.licdn.com/dms/image/C5603AQHnWP2pLXNElA/profile-displayphoto-shrink_200_200/0?e=1597881600&v=beta&t=4mkgFZn0Ny3TO2vC6IA0atRSJNjrhA1OstP0kSkDdtc" width=200> | <img src="https://media-exp1.licdn.com/dms/image/C5603AQF1rn6d_fEWRQ/profile-displayphoto-shrink_200_200/0?e=1597881600&v=beta&t=5_hQV3iFj87RiQZzLMr76c7G63yL8O4PI29KeBsgbqw" width=200> |
| [<img src="https://image.flaticon.com/icons/svg/25/25231.svg" width=25>](https://github.com/aklefebvere) [<img src = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.shareicon.net%2Fdata%2F2017%2F06%2F30%2F888065_logo_512x512.png&f=1&nofb=1" width=27>](https://www.linkedin.com/in/adriann-lefebvere-6571761a3/) | [<img src="https://image.flaticon.com/icons/svg/25/25231.svg" width=25>](https://github.com/cjakuc) [<img src = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.shareicon.net%2Fdata%2F2017%2F06%2F30%2F888065_logo_512x512.png&f=1&nofb=1" width=27>](https://www.linkedin.com/in/chrisjakuc/) |

Future web team members: If you have any problems with our API or have any questions, you can contact either of us via Slack and we will help troubleshoot/answer any questions.

## Local Setup
* Clone this repo and cd into the directory
* `pipenv install` to create the pip enviroment
* `pipenv shell` to enter the pip enviroment
* `uvicorn main:app --reload` to run the server locally

## Tech Stack
Languages: Python, SQL, HTML

Framework: FastAPI

Deployment: AWS Elastic Beanstalk

Database: PostgreSQL hosted with ElephantSQL
* ElephantSQL login information can be found in the PVD

## API Documentation
The API documentation can be found in the deployed version of the API [here](https://api.budgetblocks.org/docs)

## Communicating with the API

### /transactions
* The transaction object comes from the get request from the PLAID API (dealt on the web side).

  * Specifically, the "transactions" key from the transaction object from the PLAID API

* specifying the `user_id` key tells the API to use that user's categorical preferences.
  * If a `user_id` doesn't exist in the database, the API creates the user in the users table and gives that user the default budget blocks categories.

### /census
* Web team will grab the location from the user's account on Budget Blocks and pass the location parameters to the `location` key.
  * The parameters must have a city and state (abbreviation or full name), zipcode does not work with the API.

* Specifying the `user_id` tells the API to use the users categorical preferences to categorize the census data to their preferences.

### /update_users
* `Plaid_cats` is needed so the API knows what PLAID category it's going to be moving.

* `old_BB` is the current location of the PLAID category which is the value of the key `Plaid_cats`

* `new_BB` is the location where that user wants to move that PLAID category to.

* specifying the `user_id` will re-categorize a specific transaction for just that user.
  * __When the user has changed a transaction category, that user will not get the latest updates from the master categories if they are changed__

### /admin routes
* `/admin` is a route to all the admin routes to our API
  * Login information will be stored in the PVD

* `/admin/reset_user` and `/admin/reset_master` will completely wipe all changed data that was created and will set everything back to "factory defaults"
  * There is a conformation if you are accessing the `/reset_master` or `/reset_user` through the admin panel just in case you click on it by accident.
  
* when using `/admin/edit_master` the separate plaid categories are noted by the word `AND` in all caps.
  * example: `Bar AND Sports Bar`, `Sports Bar` is a sub category of `Bar` in PLAID.
 
