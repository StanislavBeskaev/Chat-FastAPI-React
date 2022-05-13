import React from 'react'
import {Spinner} from 'react-bootstrap'

//TODO сделать loader побольше
const Loader = () => {
  return (
    <>
      <Spinner animation="border" variant="primary" className="mt-5 ms-5 me-3" />
      Загрузка данных
    </>

  )
}

export default Loader