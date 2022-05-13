import React, {useContext} from 'react'
import {Redirect, Route, Switch} from 'react-router-dom'
import {observer} from 'mobx-react-lite'

import {AuthContext} from '../context'
import {privateRoutes, publicRoutes} from '../router'
import Loader from './UI/Loader/Loader'


const AppRouter = () => {
  const {store, fetchUserInfo} = useContext(AuthContext)

  console.log("fetchUserInfo", fetchUserInfo)

  if (fetchUserInfo) {
    return <Loader />
  }

  return (
    store.isAuth
      ?
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