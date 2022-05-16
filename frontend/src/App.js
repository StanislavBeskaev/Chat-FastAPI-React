import React, {useEffect, useState} from 'react'
import {BrowserRouter} from 'react-router-dom'
import {observer} from 'mobx-react-lite'

import AppRouter from './components/AppRouter'
import {AuthContext} from './context'
import store from './stores/store'


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
      fetchUserInfo
    }}>
      <BrowserRouter>
        <AppRouter/>
      </BrowserRouter>
    </AuthContext.Provider>
  )
}

export default observer(App)
