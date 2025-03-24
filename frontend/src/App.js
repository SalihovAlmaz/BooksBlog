// import './App.css';
import axios from "axios";
import React from 'react';

class App extends React.Component{
    state = {details: [],}

    componentDidMount() {
    let data;
    axios.get('http://localhost:8000')
        .then(res => {
            data = res.data.results; // Извлекаем массив из ключа 'results'
            if (Array.isArray(data)) {
                this.setState({
                    details: data
                });
            } else {
                console.error("Ошибка: Данные не являются массивом.");
            }
        })
        .catch(err => {
            console.log(err);
        })
}
    render() {
        return (
    <div>
      <h1>Список книг</h1>
      <ul>
          {this.state.details.map((output, id) => (
              <div key={id}>
                  <div>
                      <h2>{output.title}</h2>
                      <p>{output.description}</p>
                  </div>
              </div>
          ))}
      </ul>
    </div>
  )
    }
}

export default App;










