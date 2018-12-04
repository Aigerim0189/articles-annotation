import React from 'react'
import axios from 'axios'

import Panel from 'react-bootstrap/es/Panel'
import Grid from 'react-bootstrap/lib/Grid'
import FormGroup from 'react-bootstrap/es/FormGroup'
import Button from 'react-bootstrap/es/Button'
import FormControl from 'react-bootstrap/es/FormControl'
import Navbar from 'react-bootstrap/es/Navbar'
import ListGroup from "react-bootstrap/es/ListGroup";
import ListGroupItem from "react-bootstrap/es/ListGroupItem";
import Label from "react-bootstrap/es/Label";

export default class App extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            initialText: "",
            sentences: null,
            rakeOutput: null
        }
    }

    onInitialTextChange(e) {
        this.setState({
            initialText: e.target.value
        });
    }

    processInitialText() {
        if (this.state.initialText === "") {
            return;
        }
        axios.post('/process-initial-text', { text: this.state.initialText })
            .then(response => {
                console.log(response.data);
                this.setState({
                    sentences: response.data
                });
                this.processRake();
            })
            .catch(error => console.error(error));
    }

    processRake() {
        axios.post('/process-rake', { text: this.state.initialText })
            .then(response => {
                console.log(response.data);
                this.setState({
                    rakeOutput: response.data
                });
            })
            .catch(error => console.error(error))
    }

    render() {
        return (
            <div>
                <Navbar>
                    <Navbar.Header>
                        <Navbar.Brand>
                            <a href="#">articles-annotation</a>
                        </Navbar.Brand>
                    </Navbar.Header>
                </Navbar>
                <Grid>

                    <Panel>
                        <Panel.Heading>
                            <Panel.Title>1. Исходный текст</Panel.Title>
                        </Panel.Heading>
                        <Panel.Body>
                            <FormGroup controlId="initialText">
                                <FormGroup controlId="initialText">
                                    <FormControl
                                        componentClass="textarea"
                                        placeholder="Введите исходный текст"
                                        value={this.state.initialText}
                                        onChange={this.onInitialTextChange.bind(this)}
                                    />
                                </FormGroup>
                                <br />
                                <Button onClick={this.processInitialText.bind(this)}>
                                    Обработать
                                </Button>
                            </FormGroup>
                        </Panel.Body>
                    </Panel>

                    {this.state.sentences &&
                    <Panel>
                        <Panel.Heading>
                            <Panel.Title toggle>2. Предложения</Panel.Title>
                        </Panel.Heading>
                        <Panel.Body collapsible>
                            <ListGroup>
                                {Object.keys(this.state.sentences)
                                    .sort(function (a, b) {
                                            let aFirst = parseInt(a.split(', ')[0]);
                                            let bFirst = parseInt(b.split(', ')[0]);
                                            if (aFirst > bFirst) return 1;
                                            return -1;
                                        })
                                    .map(key => 
                                        <ListGroupItem key={key}>
                                            {key + ': ' + this.state.sentences[key]}
                                        </ListGroupItem>
                                    )}
                            </ListGroup>
                        </Panel.Body>
                    </Panel>}

                    {this.state.rakeOutput &&
                    <Panel>
                        <Panel.Heading>
                            <Panel.Title toggle>3. Rake</Panel.Title>
                        </Panel.Heading>
                        <Panel.Body collapsible>
                            <ListGroup>
                                {this.state.rakeOutput.map((item, index) =>
                                        <ListGroupItem key={index}>
                                            {item}
                                        </ListGroupItem>
                                    )}
                            </ListGroup>
                        </Panel.Body>
                    </Panel>}

                </Grid>
            </div>
        );
    }

}
