import React, {useContext} from 'react'
import {Redirect, Route, Switch} from 'react-router-dom'
import {observer} from 'mobx-react-lite'

import {AuthContext} from '../context'
import {privateRoutes, publicRoutes} from '../router'
import authStore from '../stores/authStore'
import Loader from './UI/Loader/Loader'
import {SocketProvider} from '../contexts/SocketProvider'
import Sidebar from './Sidebar'


const AppRouter = () => {
  const {fetchUserInfo} = useContext(AuthContext)

  console.log("fetchUserInfo", fetchUserInfo)

  if (fetchUserInfo) {
    return <Loader />
  }

  return (
    authStore.isAuth
      ?
      <SocketProvider login={authStore.user.login}>
        <div className="d-flex" style={{height: '100vh'}}>
          <Sidebar login={authStore.user.login}/>
          <Switch>
            {privateRoutes.map(route =>
              <Route
                component={route.component}
                path={route.path}
                exact={route.exact}
                key={route.path}
              />
            )}
            <Redirect to='/'/>
          </Switch>
        </div>
      </SocketProvider>
      :
      <Switch>
        {publicRoutes.map(route =>
          <Route
            component={route.component}
            path={route.path}
            exact={route.exact}
            key={route.path}
          />
        )}
        <Redirect to='/login'/>
      </Switch>
  )
}

export default observer(AppRouter)