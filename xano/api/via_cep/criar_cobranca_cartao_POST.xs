query criar_cobranca_cartao verb=POST {
  api_group = "ViaCEP"

  input {
    text customer_id? filters=trim
    text payment_token? filters=trim
    decimal value?
  }

  stack {
    api.request {
      url = "https://api-sandbox.asaas.com/v3/payments"
      method = "POST"
      params = {}
        |set:"customer":$input.customer_id
        |set:"billingType":"CREDIT_CARD"
        |set:"value":$input.value
        |set:"dueDate":(now
          |transform_timestamp:"+1 day"
          |format_timestamp:"Y-m-d":"UTC"
        )
        |set:"creditCardToken":$input.payment_token
      headers = []
        |push:"accept: application/json"
        |push:"content-type: application/json"
        |push:"access_token:$aact_hmlg_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OjFiODM1OWVhLWQ5M2YtNGJmYy04NjA1LWUxZjQ0ODczMmM0Yjo6JGFhY2hfYjFjYmY3MTAtN2ZlMS00NDgyLTk2ZmYtYTlkOTU2ZDFhMzMy"
        |push:"User-Agent: Xano"
    } as $api1
  }

  response = $api1
  guid = "uiKxsdrx2s4a09_FeuWWcutSXcA"
}