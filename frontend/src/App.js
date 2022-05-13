import React, {useEffect, useState} from 'react'
import {BrowserRouter} from 'react-router-dom'
import {observer} from 'mobx-react-lite'

import {store} from './index'
import AppRouter from './components/AppRouter'
import {AuthContext} from './context'


function App() {
  const [fetchUserInfo, setFetchUserInfo] = useState(true)

  useEffect(() => {
    setTimeout(async () => {
      if (localStorage.getItem('token')) {
        await store.checkAuth()
      }
      setFetchUserInfo(false)
    }, 700)
  }, [])

  return (
    <AuthContext.Provider value={{
      fetchUserInfo,
      store
    }}>
      <BrowserRouter>
        <AppRouter/>
      </BrowserRouter>
    </AuthContext.Provider>
  )
}

export default observer(App)
