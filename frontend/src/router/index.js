import Main from '../pages/Main/Main'
import Login from '../pages/Login/Login'
import Register from '../pages/Register/Register'


export const privateRoutes = [
    {path: '/', component: Main, exact: true},

]

export const publicRoutes = [
    {path: '/login', component: Login, exact: true},
    {path: '/register', component: Register, exact: true},
]
