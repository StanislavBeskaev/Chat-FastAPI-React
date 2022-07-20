import React, {useState, useEffect} from 'react'
import {Button} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import messagesStore from '../../stores/messagesStore'


const Search = () => {
  const [element, setElement] = useState(null)
  const [count, setCount] = useState(null)
  const [ids, setIds] = useState([])
  const [current, setCurrent] = useState(0)

  const changeElement = newElement => {
    dropSelection()

    if (!newElement) return

    newElement.scrollIntoView({block: "center"})
    newElement.parentElement.style.border = '3px solid dodgerblue'
    newElement.parentElement.style.borderRadius = '8px'
    newElement.parentElement.style.padding = '3px'
    setElement(newElement)
  }

  useEffect(() => {
    if (ids.length >= 0) {
      changeElement(document.getElementById(ids[current]))
    }
  }, [current])

  const increaseCurrent = () => {
    if (!count || current === (count - 1)) return
    setCurrent(prevCurrent => prevCurrent + 1)
  }

  const decreaseCurrent = () => {
    if (!count || current === 0) return
    setCurrent(prevCurrent => prevCurrent - 1)
  }

  const dropSelection = () => {
    if (element) element.parentElement.style.border = null
  }

  const searchMessage = e => {
    console.log('searchMessage')
    console.log(element)
    dropSelection()

    const text = e.target.value
    if (!text) {
      setCount(null)
      setCurrent(0)
      setElement(null)
      return
    }

    console.log('Ищем текст:', text)
    const messagesIds = messagesStore.getMessagesIdsWithTextInCurrentChat(text)
    setIds(messagesIds)
    setCount(messagesIds.length)
    setCurrent(0)

    if (messagesIds.length > 0) {
      const firstMessage = document.getElementById(messagesIds[0])
      console.log(firstMessage)
      changeElement(firstMessage)
    }
  }

  return (
    <>
      {
        count
          ? <div className="d-flex gap-2 align-items-center">
              <span>{current + 1}/{count}</span>
              <Button
                variant="light"
                size="sm"
                onClick={decreaseCurrent}
              >
                &#8593;
              </Button>
              <Button
                variant="light"
                size="sm"
                onClick={increaseCurrent}
              >
                &#8595;
              </Button>
            </div>
          : null
      }
      <input
        type="text"
        onChange={searchMessage}
      />
    </>
  )
}

export default observer(Search)