## Africastalking Code Challange

A running version of the app can be accessed on the AfricasTalking sandbox dial `*384*9240#`

# Installation

Ensure you have docker and docker compose installed

#### Set your africastalking Username, productName, ApiKey, providerChannel
Create a file named `.env` on the same directory as the docker-compose.yml
and add the following
```bash
$ cat > .env <<EOF
> # app_env.env
> # your africastalking creds
> # your africastalking account username
> AT_USERNAME=sandbox
> 
> # set this to production when on production
> AT_ENVIRONMENT=sandbox
> 
> # your africatslaking account api key
> AT_APIKEY=your account apikey
> 
> # your africastalking sms sender id
> AT_SENDER_ID=your account sender id
> 
> # africatalking payments gateway
> AT_PRODUCT_NAME=your accounts product name
> AT_PROVIDER_CHANNEL=your at provider channel
> EOF
```

#### Spin up the application
```bash
$ docker compose up
```

The ussd callback will be at

[http://localhost/ussd](http://localhost/ussd)

You can tunnel this port through ngrok and use it to receive on Africastalking platform