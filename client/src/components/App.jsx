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

function occurrences(string, subString, allowOverlapping=false) {
    string += "";
    subString += "";
    if (subString.length <= 0) return (string.length + 1);

    let n = 0,
        pos = 0,
        step = allowOverlapping ? 1 : subString.length;

    while (true) {
        pos = string.indexOf(subString, pos);
        if (pos >= 0) {
            ++n;
            pos += step;
        } else break;
    }
    return n;
}

export default class App extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            initialText: "",
            sentences: null,
            keywords: null,
            verbs: null,
            nouns: null,
            connectors: null,
            weights: null
        };

        this.processRake = this.processRake.bind(this);
        this.getVerbs = this.getVerbs.bind(this);
        this.getNouns = this.getNouns.bind(this);
        this.getConnectors = this.getConnectors.bind(this);
        this.countWeights = this.countWeights.bind(this);
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
                }, () => this.processRake());
            })
            .catch(error => console.error(error));
    }

    processRake() {
        axios.post('/process-rake', { text: this.state.initialText })
            .then(response => {
                this.setState({
                    keywords: response.data
                }, () => {
                    console.log("Get verbs");
                    this.getVerbs()
                });
            })
            .catch(error => console.error(error))
    }

    getVerbs() {
        axios.get('/get-verbs')
            .then(response => {
                console.log(response.data);
                this.setState({
                    verbs: response.data
                }, () => this.getNouns());
            })
            .catch(error => console.error(error))
    }

    getNouns() {
        axios.get('/get-nouns')
            .then(response => {
                console.log(response.data);
                this.setState({
                    nouns: response.data
                }, () => this.getConnectors());
            })
            .catch(error => console.error(error))
    }

    getConnectors() {
        axios.get('/get-connectors')
            .then(response => {
                console.log(response.data);
                this.setState({
                    connectors: response.data
                }, () => this.countWeights());
            })
            .catch(error => console.error(error))
    }

    countWeights() {
        let weights = [];
        let info = [];

        let keys = Object.keys(this.state.sentences);
        let sentences = Object.values(this.state.sentences);
        for (let i = 0; i < sentences.length; ++i) {
            let sentence_info = {};
            sentence_info['key'] = keys[i];
            sentence_info['text'] = sentences[i];

            // For each sentence find keywords in it
            let wKeywords = 0;
            for (let j = 0; j < this.state.keywords.length; ++j) {
                let occ = occurrences(sentences[i], this.state.keywords[j]);
                wKeywords += 10 * occ;
                if (occ > 0) {
                    sentence_info[this.state.keywords[j]] = 10;
                }
            }
            let totalKeywords = this.state.keywords.length !== 0
                ? wKeywords * 1. / this.state.keywords.length
                : 0;

            // For each sentence find verbs in it
            let wVerbs = 0;
            for (let j = 0; j < this.state.verbs.length; ++j) {
                let occ = occurrences(sentences[i], this.state.verbs[j][0]);
                wVerbs += this.state.verbs[j][1] * occ;
                if (occ > 0) {
                    sentence_info[this.state.verbs[j][0]] = this.state.verbs[j][1];
                }
            }

            // For each sentence find nouns in it
            let wNouns = 0;
            for (let j = 0; j < this.state.nouns.length; ++j) {
                let occ = occurrences(sentences[i], this.state.nouns[j][0]);
                wNouns += this.state.nouns[j][1] * occ;
                if (occ > 0) {
                    sentence_info[this.state.nouns[j][0]] = this.state.nouns[j][1];
                }
            }
            let totalVerbsAndNouns = (this.state.verbs.length + this.state.nouns.length) !== 0
                ? (wVerbs + wNouns) * 1. / (this.state.verbs.length + this.state.nouns.length)
                : 0;

            // For each sentence find connectors in it
            let wConnectors = 0;
            for (let j = 0; j < this.state.connectors.length; ++j) {
                let occ = occurrences(sentences[i], this.state.connectors[j][0]);
                wConnectors += 5 * occ;
                if (occ > 0) {
                    sentence_info[this.state.connectors[j][0]] = 5;
                }
            }
            let totalConnectors = this.state.connectors.length !== 0
                ? wConnectors * 1. / this.state.connectors.length
                : 0;

            console.log(totalKeywords);
            console.log(totalVerbsAndNouns);
            console.log(totalConnectors);

            weights[i] = (totalKeywords + totalVerbsAndNouns + totalConnectors).toFixed(4);
            sentence_info['weight'] = weights[i];
            info[i] = sentence_info;
        }

        this.setState({
            weights: weights
        });
        console.log(info);

        axios.post('/save-info', {'info': info}).then(() => {}).catch(() => {});
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

                    {this.state.weights &&
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
                                    .map((key, index) =>
                                        <ListGroupItem key={key}>
                                            {key + ': ' + this.state.sentences[key]}
                                            <br /><br />
                                            {'Вес: ' + this.state.weights[index]}
                                        </ListGroupItem>
                                    )}
                            </ListGroup>
                        </Panel.Body>
                    </Panel>}

                    {this.state.keywords &&
                    <Panel>
                        <Panel.Heading>
                            <Panel.Title toggle>3. Rake</Panel.Title>
                        </Panel.Heading>
                        <Panel.Body collapsible>
                            <ListGroup>
                                {this.state.keywords.map((item, index) =>
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
