import Login from '../pages/Login/Login'
import Register from '../pages/Register/Register'
import UserData from '../pages/UserData/UserData'
import Main from '../pages/Main/Main'


export const privateRoutes = [
    {path: '/', component: Main, exact: true},
    {path: '/user-data/', component: UserData, exact: true},
]

export const publicRoutes = [
    {path: '/login', component: Login, exact: true},
    {path: '/register', component: Register, exact: true},
]
