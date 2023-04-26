const signaturePayload = "\"{\\\"mobileNumber\\\":\\\"9642429378\\\",\\\"mobileCountryCode\\\":\\\"+91\\\",\\\"merchantId\\\":\\\"NAMMA_YATRI\\\",\\\"timestamp\\\":\\\"2023-04-13T07:28:40+00:00\\\"}\"";
let signature = "C7WK+z3aRyW7WaUA24K1zt5Kl+ONrMouYBiB+qHpZZAZamF4+6sZmCJMZZdw9zVyDIBnyMukeKnQLNZW+WXxdozrsgOUl6qDee384PIi6QInBD46hUTRtn4SSmaLQ+EGdneiC4UbM5aH2lnFy48VO4pUqx2jkdsjaVtHLe68gLqWivXuBTF9I0jUq/m/IceZHHikJwCTxQdx8r+wjNEdhLOJIs8Q4TQYENvjW1NjAcCZDH8DkU6e1qooGU3GQovYCTxx1yPZcFq9U95JAnpOo4o4kpnQSzNVsFfX6ntvi8SlravtJQyhMF/MAr6kqVUJeVKmAgqSjpYSaIxp2Wm6lA=="

fetch('http://127.0.0.1:8013/v2/auth', {
    method: 'POST',
    body: signaturePayload,
    headers: {
        'x-sdk-authorization': signature,
        'Content-Type': 'application/json;charset=utf-8'
    }
})
.then((response) => response.json())
.then((json) => console.log(json));