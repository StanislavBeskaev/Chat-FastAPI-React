import React from 'react'
import ReactDOM from 'react-dom/client'
import 'bootstrap/dist/css/bootstrap.min.css'

import App from './App'
import Store from './store/store'

export const store = new Store()

const root = ReactDOM.createRoot(document.getElementById('root'))
root.render(
    <App/>
)
