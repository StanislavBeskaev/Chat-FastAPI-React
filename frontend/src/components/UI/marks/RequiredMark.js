import React from 'react'

const RequiredMark = ({required}) => {
  return (
    <>
      {required
        ? <span style={{color: "red"}}>*</span>
        : null
      }
    </>
  )
}

export default RequiredMark