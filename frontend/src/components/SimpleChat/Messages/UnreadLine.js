import React, {useCallback} from 'react'

const UnreadLine = () => {
  const setRef = useCallback(node => {
    if (node) {
      node.scrollIntoView({smooth: true, block: 'center'})
    }
  }, [])

  return (
    <div
      ref={setRef}
      className="py-1 px-2 text-primary align-self-center m-3 border border-primary"
    >
      <span className="me-2">&#8595;</span>
      Непрочитанные сообщения
      <span className="ms-2">&#8595;</span>
    </div>
  )
}

export default UnreadLine