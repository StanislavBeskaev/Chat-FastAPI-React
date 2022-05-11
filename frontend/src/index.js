import React, {createContext} from 'react'
import ReactDOM from 'react-dom/client'
import 'bootstrap/dist/css/bootstrap.min.css'

import App from './App'
import Store from './store/store'


export const store = new Store()
export const Context = createContext({
  store,
})


const root = ReactDOM.createRoot(document.getElementById('root'))
root.render(
  <Context.Provider value={{store}}>
    <App/>
  </Context.Provider>
)
