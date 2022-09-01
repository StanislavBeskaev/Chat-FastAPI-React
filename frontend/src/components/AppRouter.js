import React, {useContext} from 'react'
import {Redirect, Route, Switch} from 'react-router-dom'
import {observer} from 'mobx-react-lite'

import authStore from '../stores/authStore'
import {AuthContext} from '../context'
import Loader from './UI/Loader/Loader'
import {privateRoutes, publicRoutes} from '../router'
import Sidebar from './Sidebar/Sidebar'


const AppRouter = () => {
  const {fetchUserInfo} = useContext(AuthContext)

  console.log("fetchUserInfo", fetchUserInfo)

  if (fetchUserInfo) {
    return <Loader />
  }

  return (
    authStore.isAuth
      ?
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
