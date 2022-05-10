import React, {useContext, useEffect} from 'react'
import {Spinner} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import {Context} from './index'
import LoginPage from './components/pages/LoginPage/LoginPage'
import MainPage from './components/pages/MainPage/MainPage'


function App() {
  const {store} = useContext(Context)

  useEffect(() => {
    if (localStorage.getItem('token')) {
      console.log("checkAuth")
      store.checkAuth()
    }
  }, [])

  //TODO fetchUserInfo
  if (store.isLoading) return (<Spinner animation="border" variant="success"/>)

  if (!store.isAuth) {
    return (
      <>
        <LoginPage />
      </>
    )
  }

  return (
    <>
      <MainPage />
    </>
  )
}

export default observer(App)
